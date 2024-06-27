/** @odoo-module **/
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {Component} from "@odoo/owl";
import {cookie} from "@web/core/browser/cookie"
import {WebClient} from '@web/webclient/webclient';
import {patch} from "@web/core/utils/patch";
import {browser} from "@web/core/browser/browser";
import {useDebounced} from "@web/core/utils/timing";
import {SearchBarToggler} from "@web/search/search_bar/search_bar_toggler";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import { useEffect, useState } from "@odoo/owl";

export class Player extends Component {
    setup() {
        super.setup(...arguments);
        this.action = useService("action");
        this.rpc = useService("rpc");
    }

    async _onClick() {
        let self = this;
        let action = await this.rpc("/web/dataset/call_kw/station/open_running_station", {
            model: 'station',
            method: 'open_running_station',
            args: [],
            kwargs: {}
        })
        return this.action.doAction(action, {clearBreadcrumbs: true});
    }
}

Player.template = "Player"

patch(WebClient, {
    components: {
        ...WebClient.components,
        Player,
    },
});

export function useSearchBarToggler() {
    const ui = useService("ui");

    let isToggled = false;
    const state = useState({
        isSmall: ui.isSmall,
        showSearchBar: true,
    });
    const updateState = () => {
        state.isSmall = ui.isSmall;
        state.showSearchBar = true;
    };
    updateState();

    function toggleSearchBar() {
        isToggled = !isToggled;
        updateState();
    }

    const onResize = useDebounced(updateState, 200);
    useEffect(
        () => {
            browser.addEventListener("resize", onResize);
            return () => browser.removeEventListener("resize", onResize);
        },
        () => []
    );

    return {
        state,
        component: SearchBarToggler,
        get props() {
            return {
                isSmall: state.isSmall,
                showSearchBar: state.showSearchBar,
                toggleSearchBar,
            };
        },
    };
}




patch(KanbanController.prototype, {
    setup(attributes) {
        super.setup(...arguments);
        this.searchBarToggler = useSearchBarToggler();
    }
})

if ('mediaSession' in navigator) {

    navigator.mediaSession.metadata = new MediaMetadata({
        title: '',
        artist: '',
        album: '',
        artwork: [{src: 'https://dummyimage.com/512x512', sizes: '512x512', type: 'image/png'},]
    });
}

if (!cookie.get("id_station")) {
    cookie.set("id_station", 10566);
}
if (!cookie.get("station_url")) {
    cookie.set("station_url", "https://live.humorfm.by:8443/avtoradio")
}
if (!cookie.get("station_name")) {
    cookie.set("station_name", "")
}
if (!cookie.get("station_favicon")) {
    cookie.set("station_favicon", "/web/image?model=station&amp;field=favicon&amp;id=10514")
}

let is_first_load = true;

function updateAudio() {
    let url = cookie.get("station_url");
    let name = cookie.get("station_name").replace('\"', '').replace('"', '');
    let favicon = cookie.get("station_favicon").replace('\"', '').replace('"', '');

    let audio = document.getElementById("audio");
    if (audio && !audio.paused && !is_first_load && audio.src !== url) {
        $('audio').attr("src", url);
        audio.pause();
        audio.play();
    } else if (audio && audio.src !== url) {
        $('audio').attr("src", url);
    }
    is_first_load = false;

    let audio_img = $('#audio_img');
    audio_img.attr("src", favicon);

    let audio_name = $('#audio_name');
    audio_name.text(name);

    navigator.mediaSession.metadata.title = name;
    navigator.mediaSession.metadata.artwork = [
        {src: favicon, sizes: '512x512', type: 'image/png'},
    ];
}

cookieStore.addEventListener("change", (event) => {
    updateAudio();
});

// Remove unnecessary menu items
const userMenuRegistry = registry.category("user_menuitems");
userMenuRegistry.remove("documentation");
userMenuRegistry.remove("support");
userMenuRegistry.remove("shortcuts");
userMenuRegistry.remove("separator");
userMenuRegistry.remove("odoo_account");
userMenuRegistry.remove("log_out");

screen.orientation.addEventListener("change", () => {
  console.log(`The orientation of the screen is: ${screen.orientation}`);
});

window.screen.orientation.lock("portrait");

