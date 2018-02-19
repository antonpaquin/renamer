import os
import re
from flask import Flask, render_template, send_from_directory, request
import sqlite3

app = Flask(__name__, static_url_path='')

default_src_path = '/home/anton/Media/pictures'
default_dest_path = '/home/anton/Media/pictures-anime'


conn = sqlite3.connect('files.db')


class Inode:
    inode_id_lookup = {}

    def __init__(self, fullpath):
        self.fullpath = fullpath
        # basename behaves odd for directories
        self.name = fullpath[len(os.path.dirname(fullpath))+1:]
        if os.path.isdir(fullpath):
            self.type = 'd'
        elif os.path.islink(fullpath):
            self.type = 'l'
        elif os.path.isfile(fullpath):
            self.type = 'f'
        else:
            self.type = '?'

        self.iid = 0
        self.hidden = False
        self.sql_sync()
        Inode.inode_id_lookup[self.iid] = self

    def sql_sync(self):
        name_key = str(self.fullpath.__hash__())
        c = conn.cursor()
        c.execute('SELECT rowid, hidden FROM files WHERE name_hash = ?', (name_key,))
        row = c.fetchone()
        if row:
            self.iid = row[0]
            self.hidden = bool(row[1])
        else:
            c.execute('INSERT INTO files(name_hash, hidden) VALUES (?, 0)', (name_key,))
            c.execute('SELECT rowid FROM files WHERE name_hash = ?', (name_key,))
            row = c.fetchall()
            self.iid = row[0][0]
            self.hidden = False
        c.close()

    def hide(self):
        c = conn.cursor()
        c.execute('UPDATE files SET hidden = 1 WHERE rowid = ?', (self.iid,))
        c.close()
        self.hidden = True

    def delete(self):
        os.remove(self.fullpath)

    def mvln(self, dest):
        if not os.path.exists(os.path.dirname(dest)):
            raise RuntimeError('mvln: dest path doesn\'t exist')
        if not os.path.isfile(self.fullpath):
            raise RuntimeError('mvln: src doesn\'t exist')
        if os.path.isfile(dest):
            raise RuntimeError('mvln: won\'t overwrite a file')
        if os.path.islink(self.fullpath):
            raise RuntimeError('mvln: src is already a link')

        os.rename(self.fullpath, dest)
        os.link(dest, self.fullpath)

    def extension(self):
        return self.name[self.name.rfind('.')+1:]

    @staticmethod
    def from_id(iid) -> 'Inode':
        return Inode.inode_id_lookup.get(iid, None)


class Show:
    show_name_lookup = {}

    def __init__(self, fullpath):
        self.fullpath = fullpath
        # basename behaves odd for directories
        self.name = fullpath[len(os.path.dirname(fullpath))+1:]
        self.seasons = os.listdir(self.fullpath)
        self.seasons.sort()

        Show.show_name_lookup[self.name] = self

    def episode_name(self, season: str, episode: int, extension: str):
        try:
            snum = int(re.search('[0-9]+', season).group())
        except AttributeError:
            snum = 0

        episode_name = '{showname} - s{snum:02d}e{enum:02d}.{extension}'.format(
            showname=self.name,
            snum=snum,
            enum=episode,
            extension=extension
        )
        season_path = os.path.join(self.fullpath, season)

        if not os.path.isdir(season_path):
            raise RuntimeError('Season is not there for show')

        return os.path.join(season_path, episode_name)

    @staticmethod
    def from_name(name) -> 'Show':
        return Show.show_name_lookup.get(name, None)


@app.route('/')
def main():
    nodes = []
    for ff in os.listdir(default_src_path):
        nodes.append(Inode(os.path.join(default_src_path, ff)))
    nodes = list(filter(lambda n: not n.hidden, nodes))
    nodes.sort(key=lambda n: (n.type, n.name))

    shows = []
    for ff in os.listdir(default_dest_path):
        shows.append(Show(os.path.join(default_dest_path, ff)))

    return render_template('main.html.j2', nodes=nodes, shows=shows)


@app.route('/static/<path:path>')
def route_static(path):
    return send_from_directory('static', path)


@app.route('/mvln_target')
def mvln_target():
    iid = int(request.args.get('id', None))
    sshow = request.args.get('show', None)
    season = request.args.get('season', None)
    episode = int(request.args.get('episode', None))

    if not all([iid, sshow, season, episode]):
        return '', 400

    show = Show.from_name(sshow)
    src_file = Inode.from_id(iid)
    src_file.mvln(show.episode_name(season, episode, src_file.extension()))

    return 'success'


@app.route('/hide_target/<int:iid>')
def hide_target(iid):
    Inode.from_id(iid).hide()
    return ''


@app.route('/delete_target/<int:iid>')
def delete_target(iid):
    Inode.from_id(iid).delete()
    return ''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8114)
