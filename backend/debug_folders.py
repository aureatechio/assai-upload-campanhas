import os

def debug_campaign_structure():
    campaigns_dir = r"G:\Drives compartilhados\__JOBS 2025\_ASSAI\_ROBO ASSAI\MIDIAS"
    campaign_name = "ANIVERSARIO REGIONAIS"
    campaign_path = os.path.join(campaigns_dir, campaign_name)

    print(f"Campaign path: {campaign_path}")
    print(f"Exists: {os.path.exists(campaign_path)}")
    print()

    if os.path.exists(campaign_path):
        print("Main folders:")
        items = os.listdir(campaign_path)
        for item in items:
            item_path = os.path.join(campaign_path, item)
            is_dir = os.path.isdir(item_path)
            print(f"  {item} {'(DIR)' if is_dir else '(FILE)'}")
        print()

        # Check specific folders
        folders_to_check = ['CABECAS', 'BG', 'ASSINATURAS', 'TRILHA']

        for folder in folders_to_check:
            folder_path = os.path.join(campaign_path, folder)
            print(f"Checking {folder}:")
            print(f"  Path: {folder_path}")
            print(f"  Exists: {os.path.exists(folder_path)}")

            if os.path.exists(folder_path):
                subfolders = os.listdir(folder_path)
                print(f"  Contents: {subfolders}")

                # For CABECAS, check state folders
                if folder == 'CABECAS':
                    for subfolder in subfolders:
                        subfolder_path = os.path.join(folder_path, subfolder)
                        if os.path.isdir(subfolder_path):
                            print(f"    State: {subfolder}")
                            files = os.listdir(subfolder_path)
                            media_files = [f for f in files if f.lower().endswith(('.mp4', '.mp3', '.wav'))]
                            print(f"      Media files: {media_files}")

                # For BG, check subfolders
                elif folder == 'BG':
                    for subfolder in subfolders:
                        subfolder_path = os.path.join(folder_path, subfolder)
                        if os.path.isdir(subfolder_path):
                            print(f"    BG Type: {subfolder}")
                            files = os.listdir(subfolder_path)
                            media_files = [f for f in files if f.lower().endswith(('.mp4', '.mp3', '.wav'))]
                            print(f"      Media files: {media_files}")

                # For ASSINATURAS, check subfolders
                elif folder == 'ASSINATURAS':
                    for item in subfolders:
                        item_path = os.path.join(folder_path, item)
                        if os.path.isdir(item_path):
                            print(f"    ASSINATURAS folder: {item}")
                            files = os.listdir(item_path)
                            media_files = [f for f in files if f.lower().endswith(('.mp4', '.mp3', '.wav'))]
                            print(f"      Media files: {media_files}")
                        else:
                            if item.lower().endswith(('.mp4', '.mp3', '.wav')):
                                print(f"    Direct media file: {item}")

                # For TRILHA, check files directly
                elif folder == 'TRILHA':
                    media_files = [f for f in subfolders if f.lower().endswith(('.mp4', '.mp3', '.wav'))]
                    print(f"    Direct media files: {media_files}")
            print()

if __name__ == "__main__":
    debug_campaign_structure()