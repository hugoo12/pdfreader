import os

base_folder = r"C:\Users\hugoo\Desktop\Pdf"  # or wherever your bins live

for entry in os.listdir(base_folder):
    subdir = os.path.join(base_folder, entry)
    if os.path.isdir(subdir):
        # list only the files in this subdir
        files = [
            name for name in os.listdir(subdir)
            if os.path.isfile(os.path.join(subdir, name))
        ]
        print(f"{entry}: {len(files)} files")
