function do_delete(elem, file_id) {
    var state = elem.attributes['state'].value;

    if (state === 'init') {
        elem.setAttribute('state', 'confirm');
        elem.value = 'Confirm?';
        elem.onblur = function() {
            if (state === 'confirm') {
                elem.value = 'Delete';
                elem.setAttribute('state', 'init');
            }
        };
    }

    if (state === 'confirm') {
        elem.setAttribute('state', 'deleting');
        elem.value = '...';

        var req = new XMLHttpRequest();
        req.open('GET', '/delete_target/' + file_id);
        req.onload = function() {
            finish_delete(elem, file_id);
        };
        req.send();
    }
}

function finish_delete(elem, file_id) {
    var state = elem.attributes['state'].value;

    if (state === 'deleting') {
        elem.setAttribute('state', 'deleted');
        elem.value = 'Deleted';
        elem.setAttribute('onclick', null);
        elem.parentElement.parentElement.classList.add('deleted');
    }
}

function do_hide(elem, file_id) {
    var req = new XMLHttpRequest();
    req.open('GET', '/hide_target/' + file_id);
    req.onload = function() {
        finish_hide(elem, file_id);
    };
    req.send();
}

function finish_hide(elem, file_id) {
    elem.parentElement.parentElement.classList.add('deleted');
}

function do_mvln(elem, file_id) {
    var show_select = elem.parentElement.children[0];
    var season_select = elem.parentElement.children[1];
    var episode_input = elem.parentElement.children[2];

    var show = show_select.value;
    var season = season_select.value;
    var episode = episode_input.value;

    elem.value = '...';

    var req = new XMLHttpRequest();
    req.open('GET', '/mvln_target?id=' + file_id + '&show=' + show + '&season=' + season + '&episode=' + episode);
    req.onload = function() {
        finish_mvln(elem, file_id, req.responseText);
    };
    req.send();
}

function finish_mvln(elem, file_id, resp) {
    if (resp === 'success') {
        elem.value = 'done';
    } else {
        elem.value = 'fail';
        console.log(resp);
    }
}

(function() {
    for (var ii=0; ii<file_ids.length; ii++) {
        var file_id = file_ids[ii];
        var btn_mvln = document.getElementById('form-mvln-' + file_id).children[3];
        btn_mvln.onclick = (function(elem, file_id) {
            return function() {
                do_mvln(elem, file_id);
            };
        })(btn_mvln, file_id);

        var btn_hide = document.getElementById('form-hide-' + file_id).children[0];
        btn_hide.onclick = (function(elem, file_id) {
            return function() {
                do_hide(elem, file_id);
            };
        })(btn_hide, file_id);

        var btn_delete = document.getElementById('form-delete-' + file_id).children[0];
        btn_delete.onclick = (function(elem, file_id) {
            return function() {
                do_delete(elem, file_id);
            };
        })(btn_delete, file_id);
    }
})();

(function() {
    var show_selectors = document.querySelectorAll('[field=show]');
    for (var ii=0; ii<show_selectors.length; ii++) {
        var elem = show_selectors[ii];
        var guess = elem.getAttribute('guess');
        for (var jj=0; jj < shows.length; jj++) {
            var opt = document.createElement('option');
            opt.innerText = shows[jj];
            if (shows[jj] === guess) {
                opt.setAttribute('selected', 'selected');
            }
            elem.appendChild(opt);
        }
        elem.onchange = function() {
            var season_select = this.parentElement.children[1];
            while (season_select.firstChild) {
                season_select.removeChild(season_select.firstChild);
            }
            var seasons = show_seasons[this.value];
            for (var kk=0; kk<seasons.length; kk++) {
                var opt = document.createElement('option');
                opt.innerText = seasons[kk];
                season_select.appendChild(opt);
            }
        };
        elem.onchange();
    }

    var episode_selectors = document.querySelectorAll('[field=episode]');
    for (var ii=0; ii<episode_selectors.length; ii++) {
        var elem = episode_selectors[ii];
        elem.value = elem.getAttribute('guess');
    }
})();
