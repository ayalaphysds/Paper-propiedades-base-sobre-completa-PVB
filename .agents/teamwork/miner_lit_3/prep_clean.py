with open("text_villalba2023.txt", "r", encoding="utf-8") as f:
    v_lines = f.readlines()

print(f"Villalba 2023 total lines: {len(v_lines)}")

with open("text_coupling2021.txt", "r", encoding="utf-8") as f:
    c_lines = f.readlines()

print(f"Coupling 2021 total lines: {len(c_lines)}")

# Let's write out clean text to read easily
with open("villalba_clean.txt", "w", encoding="utf-8") as f:
    f.writelines(v_lines)

with open("coupling_clean.txt", "w", encoding="utf-8") as f:
    f.writelines(c_lines)

print("Files saved.")
