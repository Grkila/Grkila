import sys
p = dict(WORLD=0.06, KEY=90, RIM=160, FILL=12, CAB=18, LAMP=25, CAMLOC=(0.55, -4.7, 1.32), CAMTGT=(0.75, 0.4, 1.12),
         LENS=27, SHIFTX=0.0, SHIFTY=0.02, FSTOP=5.6, EXPO=0.0, WALLTINT=(0.2, 0.22, 0.26))
for a in sys.argv[1:]:
    k, v = a.split("=", 1); p[k] = eval(v)
s = open("look.py", encoding="utf-8").read()
for k in sorted(p, key=len, reverse=True): s = s.replace(k, repr(p[k]))
open("look_run.py", "w", encoding="utf-8").write(s)
