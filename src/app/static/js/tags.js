script = document.getElementById("tags-script");
courier_tags = JSON.parse(script.getAttribute('courier_tags').replaceAll("\'", '\"'));
available_tags = JSON.parse(script.getAttribute('available_tags').replaceAll("\'", '\"'));

console.log(courier_tags);
console.log(available_tags);

function filterTags() {

    input = document.getElementById("tags-search").value;
    list = document.getElementById("tags-container");
    tags = document.getElementsByClassName("tag");

    while (tags.length) {
        list.removeChild(tags[0]);
    }

    for (let n = 0; n < available_tags.length; n++) {
        dummy = document.createElement("div")
        dummy.innerHTML = `<div class="tag dropdown-item checkbox" role="checkbox" aria-checked="false"><svg aria-hidden="true" height="16" width="16" class="octicon octicon-check see-through"><path class="see-through" style="visibility: hidden" fill="#FFFFFF" fill-rule="evenodd" d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z"></path></svg><input hidden class="see-through" type="checkbox" name="tag-checkbox" value="${available_tags[n]}"><span class="see-through user-select-none">${available_tags[n]}</span></div>`;

        dummy.firstChild.setAttribute("aria-checked", `${courier_tags.includes(available_tags[n])}`);
        dummy.firstChild.children[1].checked = courier_tags.includes(available_tags[n]);
        if (dummy.firstChild.children[1].checked)
            dummy.firstChild.getElementsByClassName("octicon")[0].children[0].style.visibility = "visible";

        dummy.firstChild.addEventListener("click", function (evt) {
            let e = evt.currentTarget
            if (e.getAttribute("aria-checked") == "false") {
                e.setAttribute("aria-checked", "true");
                e.getElementsByClassName("octicon")[0].children[0].style.visibility = "visible";
                e.children[1].checked = true;
            } else {
                e.setAttribute("aria-checked", "false");
                e.getElementsByClassName("octicon")[0].children[0].style.visibility = "hidden";
                e.children[1].checked = false;
            }
        }, true);
        list.appendChild(dummy.firstChild);
    }

    for (let n = 0; n < tags.length; n++) {
        if (!tags[n].children[2].innerText.match(new RegExp("^" + input, 'gi'))) {
            list.removeChild(tags[n]);
            n--;
        }
    }
}

$(document).ready(filterTags());