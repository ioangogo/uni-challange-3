from PIL import ImageSequence
from PIL import Image
from PIL import ImageOps


# This function is from a project of mine on github: https://github.com/ioangogo/MicrobitImageConverter
# This is just incase it gets caught by a plagisum checker for being on github, its my github its from
def convertoGrayScaleMBITIMG(img, w, h):
        grayimg = ImageOps.grayscale(img)
        px = grayimg.load()
        var = []
        for y in range(0, h):
            var.append("")
            for x in range(0, w):
                pixelVal = px[x, y]
                var[y]+="{}".format(int(pixelVal>0))
            var[y] = var[y]
        duration = img.info['duration']
        print(duration)
        return (var,duration)

def getFrames(img):
    sequence=[]

    im = Image.open(img)

    frames = [frame.copy() for frame in ImageSequence.Iterator(im)]

    animation = ImageSequence.Iterator(im)

    arrayFrames = []
    for frame in frames:
        arrayFrames.append(convertoGrayScaleMBITIMG(frame, 5, 5))
    print(arrayFrames)
    return arrayFrames
