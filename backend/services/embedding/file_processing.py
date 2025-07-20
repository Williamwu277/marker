import os

class Processor:
    def __init__(self):
        self.folder = 'storage'
        self.valid_ext = ['pdf', 'png', 'mp4']
        os.makedirs(self.folder, exist_ok=True)

    def save_document(self, file_object, file_ext, filename='storage'):
        if file_ext not in self.valid_ext: 
            raise NameError('Not a valid ext')
        
        file_path = os.path.join(self.folder, f'{filename}.{file_ext}')
        try:
            with open(file_path, 'wb') as out_file:
                out_file.write(file_object.read())
            return file_path
        except Exception as e:
            print(f"Error saving file: {e}")
            return None



