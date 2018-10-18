import argparse
import base64
import sys
import requests

def get_b64encoded_file_image(path):
    with open(path, 'rb') as img_file:
        data = img_file.read()
        return base64.b64encode(data)

def get_b64encoded_url_image(url):
    data_request = requests.get(url)
    data = data_request.content
    return base64.b64encode(data)

def display_image_in_iterm2(b64encoded_data):
    header = b'\033]1337;File=inline=1:'
    footer = b'\a\n'
    sys.stdout.buffer.write(header + b64encoded_data + footer)

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='View images/gifs in iTerm2')
    parser.add_argument('-f', '--file', help='file path of local image/gif', metavar='\b')
    parser.add_argument('-u', '--url', help='url of image/gif', metavar='\b')
    
    args = parser.parse_args()
    if args.file:
        b64encoded_data = get_b64encoded_file_image(args.file)
        display_image_in_iterm2(b64encoded_data)
    if args.url:
        b64encoded_data = get_b64encoded_url_image(args.url)
        display_image_in_iterm2(b64encoded_data)
