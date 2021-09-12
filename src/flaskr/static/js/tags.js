function filterTags(courier_tags, available_tags) {

    input = document.getElementById("tags_search").value;
    list = document.getElementById("tags-menu-list");
    tags = document.getElementsByClassName("tag-container");

    while (tags.length) {
        list.removeChild(tags[0]);
    }

    for (let n = 0; n < available_tags.length; n++) {
        container = document.createElement("div");
        container.className = "tag-container";
        container.innerText = available_tags[n];

        checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.name = "tag-checkbox";
        checkbox.parent = container;
        checkbox.value = available_tags[n];
        checkbox.checked = courier_tags.includes(available_tags[n]);

        container.insertBefore(checkbox, container.firstChild);
        list.appendChild(container);
    }

    for (let n = 0; n < tags.length; n++) {
        if (!tags[n].innerText.match(new RegExp("^" + input, 'gi'))) {
            list.removeChild(tags[n]);
            n--;
        }
    }
}

