# coding:utf-8
from uuid import uuid4
from cornice.service import Service


image = Service(name='image', path='/v0.1.0/image', description="upload image",
                cors_origins=('https://admin.keptrans.com', 'https://keptrans.com'))



@image.post()
def upload_image(request):
    up = request.up
    file = request.params.get('file')
    file_ext = '.' + file.type.split('/')[-1]
    image_url = '/products/' + uuid4().hex + file_ext
    up.put(image_url, file.file, checksum=True)
    return {'image': 'https://keptrans.b0.upaiyun.com' + image_url}
