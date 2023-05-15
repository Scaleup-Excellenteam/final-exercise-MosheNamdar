from pptx import Presentation




def read_presentation(path):
    file = Presentation(path)
    text = []
    for slide in file.slides:
        text_slide = ""
        for shape in slide.shapes:
            if shape.has_text_frame:
                for ph in shape.text_frame.paragraphs:
                    text_slide += ph.text
        text.append(text_slide)

    print(text)


def main():
    path = input("please enter a path: ")
    presentation_text = read_presentation(path)




if __name__ == '__main__':
    main()