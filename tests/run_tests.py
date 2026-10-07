"""Run all tests without pytest:  python tests/run_tests.py"""
import os, sys, importlib, time, traceback
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, '..', 'src')]
ok = fail = 0
for mod in ('test_astro', 'test_calendars', 'test_places_prayer', 'test_timeline'):
    m = importlib.import_module(mod)
    for name in sorted(n for n in dir(m) if n.startswith('test_')):
        t = time.time()
        try:
            getattr(m, name)(); ok += 1; print(f'PASS {mod}.{name} ({time.time() - t:.1f}s)')
        except Exception:
            fail += 1; print(f'FAIL {mod}.{name}'); traceback.print_exc()
print(f'\n{ok} passed, {fail} failed'); sys.exit(1 if fail else 0)
