import re

with open("backend/scripts/seed_synthetic.py", "r") as f:
    text = f.read()

replacement = """MINES = [("KDR", "Kandri", "underground", 21.416, 79.266, 300),
         ("MNS", "Mansar", "underground", 21.383, 79.250, 333),
         ("DBZ", "Dongri Buzurg", "opencast", 21.548, 79.682, 1000),
         ("BLG", "Balaghat", "underground", 21.966, 80.233, 1200),
         ("CHK", "Chikla", "underground", 21.516, 79.750, 566)]"""

text = re.sub(r'MINES = \[.*?\]', replacement, text, flags=re.DOTALL)
text = re.sub(r'# PLACEHOLDERS: verify mine names.*?\n', '', text)

with open("backend/scripts/seed_synthetic.py", "w") as f:
    f.write(text)
