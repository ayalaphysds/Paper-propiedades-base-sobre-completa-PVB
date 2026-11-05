import zipfile
from pathlib import Path

z = zipfile.ZipFile("v2/overleaf_bundle_v2.zip")
print("--- Zip Entries & Properties ---")
has_backslash = False
has_bom = False
has_abs_path = False

for info in z.infolist():
    name = info.filename
    if "\\" in name:
        has_backslash = True
        print(f"ERROR: Backslash in zip path: {name}")
    
    # Read text content if applicable
    if name.endswith((".tex", ".bib", ".cls", ".sty", ".bst", ".py")):
        raw = z.read(name)
        if raw.startswith(b"\xef\xbb\xbf"):
            has_bom = True
            print(f"WARNING: UTF-8 BOM found in: {name}")
        text = raw.decode("utf-8", errors="ignore")
        for bad in ["C:\\\\", "sayal", "AppData"]:
            if bad in text:
                print(f"WARNING: Host-specific string '{bad}' in {name}")
                has_abs_path = True

print(f"Backslash in paths: {has_backslash}")
print(f"BOM in files: {has_bom}")
print(f"Host-specific paths in source files: {has_abs_path}")

assert not has_backslash, "Zip contains Windows backslashes!"
assert not has_bom, "Files contain UTF-8 BOM!"
assert not has_abs_path, "Source code contains host-specific absolute paths!"
print("ADVERSARIAL CHECKS PASSED WITH ZERO ISSUES!")
