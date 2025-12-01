import os

root = os.path.abspath('.')
print('Scanning for training_images under', root)
found = []
for dirpath, dirnames, filenames in os.walk(root):
    if 'training_images' in dirpath:
        rel = os.path.relpath(dirpath, root)
        print('Found:', rel)
        for d in sorted(dirnames):
            pass
        files = [f for f in filenames if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        print('  image files:', len(files))
        if files:
            print('   sample:', files[:5])
        found.append(dirpath)

if not found:
    print('No training_images directory found under MyApp')
