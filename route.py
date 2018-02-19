from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def main():
    return 'hello world!'

def mvln(src, dest):
    if not os.path.exists(os.path.dirname(dest)):
        raise RuntimeError('mvln: dest path doesn\'t exist')
    if not os.path.isfile(src):
        raise RuntimeError('mvln: src doesn\'t exist')
    if os.path.isfile(dest):
        raise RuntimeError('mvln: won\'t overwrite a file')
    if os.path.islink(src):
        raise RuntimeError('mvln: src is already a link')

    os.rename(src, dest)
    os.link(dest, src)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8114)
