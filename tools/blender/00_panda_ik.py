"""Franka Panda FK/IK (kinematics.yaml from frankarobotics/franka_description).

Writes a JSON list of joint keyframes for a pick-and-place loop.
Positions are in the robot base frame (metres), tool pointing down.
"""
import json, sys
import numpy as np

H = np.pi / 2
JOINTS = [  # xyz, rpy of each joint origin relative to the previous link
    ((0, 0, 0.333), (0, 0, 0)),
    ((0, 0, 0), (-H, 0, 0)),
    ((0, -0.316, 0), (H, 0, 0)),
    ((0.0825, 0, 0), (H, 0, 0)),
    ((-0.0825, 0.384, 0), (-H, 0, 0)),
    ((0, 0, 0), (H, 0, 0)),
    ((0.088, 0, 0), (H, 0, 0)),
]
FLANGE = 0.107
HAND_YAW = -np.pi / 4
TCP = 0.1034
LO = np.array([-2.8973, -1.7628, -2.8973, -3.0718, -2.8973, -0.0175, -2.8973])
HI = np.array([2.8973, 1.7628, 2.8973, -0.0698, 2.8973, 3.7525, 2.8973])


def rpy(r, p, y):
    cr, sr, cp, sp, cy, sy = np.cos(r), np.sin(r), np.cos(p), np.sin(p), np.cos(y), np.sin(y)
    return np.array([[cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
                     [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
                     [-sp, cp * sr, cp * cr]])


def T(xyz, R):
    m = np.eye(4); m[:3, :3] = R; m[:3, 3] = xyz; return m


def rz(a):
    return T((0, 0, 0), rpy(0, 0, a))


def fk(q):
    m = np.eye(4)
    for (xyz, r), qi in zip(JOINTS, q):
        m = m @ T(xyz, rpy(*r)) @ rz(qi)
    return m @ T((0, 0, FLANGE), np.eye(3)) @ rz(HAND_YAW) @ T((0, 0, TCP), np.eye(3))


def target(p, yaw):
    # tool z points down; tool x rotated by yaw about world z
    R = rpy(np.pi, 0, 0) @ rpy(0, 0, -yaw)
    return T(p, R)


def err(m, t):
    dp = t[:3, 3] - m[:3, 3]
    Re = t[:3, :3] @ m[:3, :3].T
    w = 0.5 * np.array([Re[2, 1] - Re[1, 2], Re[0, 2] - Re[2, 0], Re[1, 0] - Re[0, 1]])
    return np.concatenate([dp, w])


def ik(t, q0, iters=400):
    q = np.array(q0, float)
    rest = np.array([q0[0], 0.2, 0, -2.3, 0, 2.5, 0.785])
    for _ in range(iters):
        e = err(fk(q), t)
        if np.linalg.norm(e) < 1e-6:
            break
        J = np.zeros((6, 7)); d = 1e-6
        for i in range(7):
            dq = q.copy(); dq[i] += d
            J[:, i] = (err(fk(q), t) - err(fk(dq), t)) / d
        lam = 0.01
        dqs = J.T @ np.linalg.solve(J @ J.T + lam * np.eye(6), e)
        N = np.eye(7) - np.linalg.pinv(J) @ J  # nullspace pull toward a natural pose
        q = np.clip(q + dqs + 0.05 * N @ (rest - q), LO + 0.05, HI - 0.05)
    return q, float(np.linalg.norm(err(fk(q), t)))


if __name__ == "__main__":
    A = np.array([0.42, -0.30]); B = np.array([0.42, 0.30])
    z_pick, z_up = 0.03, 0.22  # tcp height above desk for grasp (sponge half-height) and transfer
    yawA, yawB = np.arctan2(A[1], A[0]), np.arctan2(B[1], B[0])
    way = [  # name, xy, z, yaw, grip(0 open..1 closed), carry
        ("aboveA", A, z_up, yawA, 0, 0), ("atA", A, z_pick, yawA, 0, 0), ("gripA", A, z_pick, yawA, 1, 0),
        ("liftA", A, z_up, yawA, 1, 1), ("aboveB", B, z_up, yawB, 1, 1), ("atB", B, z_pick, yawB, 1, 1),
        ("relB", B, z_pick, yawB, 0, 0), ("liftB", B, z_up, yawB, 0, 0),
        ("home", np.array([0.32, 0.0]), 0.42, 0.0, 0, 0),
    ]
    q = np.array([0, -0.4, 0, -2.3, 0, 1.9, 0.785])
    out = []
    for name, xy, z, yaw, g, c in way:
        seed = np.array([np.arctan2(xy[1], xy[0]), 0.2, 0, -2.3, 0, 2.5, 0.785])
        q, e = ik(target((xy[0], xy[1], z), yaw), seed)
        out.append({"name": name, "q": q.round(5).tolist(), "grip": g, "carry": c, "err": e})
        print(name, np.round(q, 3), "err %.2e" % e)
    json.dump({"A": A.tolist(), "B": B.tolist(), "z_pick": z_pick, "poses": out}, open(sys.argv[1], "w"), indent=1)
