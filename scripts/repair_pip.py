import os
import sys
import subprocess
import shutil

def run(cmd):
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)

def site_packages_for_prefix(prefix):
    if os.name == "nt":
        return os.path.join(prefix, "Lib", "site-packages")
    else:
        pyver = "python{}.{}".format(sys.version_info.major, sys.version_info.minor)
        return os.path.join(prefix, "lib", pyver, "site-packages")

def main():
    exe = sys.executable
    print("Using Python executable:", exe)

    try:
        # bootstrap pip if missing/corrupted
        run([exe, "-m", "ensurepip", "--upgrade"])
    except subprocess.CalledProcessError:
        print("ensurepip failed — continuing to removal/reinstall step")

    # remove pip._vendor.rich if present (common corruption source)
    sp = site_packages_for_prefix(sys.prefix)
    pip_vendor_rich = os.path.join(sp, "pip", "_vendor", "rich")
    if os.path.exists(pip_vendor_rich):
        print("Removing pip._vendor.rich at:", pip_vendor_rich)
        try:
            shutil.rmtree(pip_vendor_rich)
        except Exception as e:
            print("Failed to remove pip._vendor.rich:", e)
            print("You may need to delete it manually then re-run this script.")
            sys.exit(1)
    else:
        print("pip._vendor.rich not found at expected location — skipping removal.")

    # upgrade pip, setuptools, wheel
    try:
        run([exe, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    except subprocess.CalledProcessError as e:
        print("pip upgrade failed:", e)
        print("If pip remains broken, try downloading get-pip.py from https://bootstrap.pypa.io/get-pip.py and run it with the venv Python.")
        sys.exit(1)

    print("Done. Try the action that previously failed (e.g. PyCharm packaging tool).")

if __name__ == "__main__":
    main()

