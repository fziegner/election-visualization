let mapGermany;  // the leaflet map
let geoJson; //the currently rendered geoJson
let info;   //control widget that shows the data in detail
let chosenInfo; // control widget that shows which element from the buildbox is currently rendered on the map
let prevNext; //control box to navigate through the buildbox on the map
let voters_mode = false;
let voters_mode_trigger_button;

let buildboxChooses = []; //array holding all geojsons that are currently selected from the buildbox
let currentIndex = 0; //the index of the array above that is currently rendered on the map

function addCard(){
        let group = $("#sortable");
        let highestNum = group.children().length;
        let newNum = highestNum + 1;

        group.append(Mustache.render(document.getElementById("addCard").innerHTML, {num: newNum}));
        $("#election_select_" + newNum).trigger("change");

        $("#btn_save").show();
}

function deleteCard(card){
    let id = parseInt(card.id.replace("close_", ""));
    $("#card_" + id).remove();

    if($("#sortable").children().length === 0){
        $("#btn_save").hide();
    }
}

function changeDrowdown(elem){
    let num = elem.id.replace("election_select_", "");
    $("#year_select_" + num).html($("#year_select_" + num).find("option").each(function(){
        if($(this).attr("election_type") != elem.value){
            $(this).attr("hidden", true);
            $(this).attr("disabled", true);
        }
        else{
            $(this).attr("hidden", false);
            $(this).attr("disabled", false);
        }
    }));
}

function saveAndRender(){
    buildboxChooses = [] //empty and refill
    let group = $("#sortable");
    let highestNum = group.children().length;
    Array.from(group.children()).forEach(function(card){
        let id = parseInt(card.id.replace("card_", ""));
        let type = $("#election_select_" + id).val();
        let year = $("#year_select_" + id).val();

        $.ajax({
            method: "get",
            url: "/data?type=" + type + "&year=" + year,
            async: false, //very important, need to wait for this ajax call to finish before continuing with the function execution
            success: function(data){
                buildboxChooses.push(data);
            },
            error: function(xhr, status, error){
                console.log(status);
                console.log(xhr);
                console.log(error);
            }
        });
    });

    currentIndex = 0;
    geoJson.removeFrom(mapGermany); //remove old geoJson
    geoJson = L.geoJSON(buildboxChooses[currentIndex], {  //render the first item from the buildbox
        style: style,
        onEachFeature: onEachFeature
    }).addTo(mapGermany);

    chosenInfo.update();
}

function renderImmediate(type, year) {
    for(let i = 0; i < buildboxChooses.length; i++){
        if(buildboxChooses[i].parameters.election_type == type && buildboxChooses[i].parameters.election_year == year){
            currentIndex = i;
            geoJson.removeFrom(mapGermany); //remove old geoJson
            geoJson = L.geoJSON(buildboxChooses[currentIndex], {  //render the next item from the buildbox
                style: style,
                onEachFeature: onEachFeature
            }).addTo(mapGermany);

            break;
        }
    }

    chosenInfo.update()
}

function renderPrev(){
    let group = $("#sortable");
    let highestNum = group.children().length;

    if(highestNum !== 0){
        if(currentIndex === 0){ //need this case separately because otherwise modulo would get negative
        currentIndex = highestNum - 1;
        }
        else {
        currentIndex = (currentIndex - 1) % highestNum; //if we had the last and click next we want to start with the first one again
        }
    }

    geoJson.removeFrom(mapGermany); //remove old geoJson
    geoJson = L.geoJSON(buildboxChooses[currentIndex], {  //render the next item from the buildbox
        style: style,
        onEachFeature: onEachFeature
    }).addTo(mapGermany);

    chosenInfo.update()
}

function renderNext(){
    let group = $("#sortable");
    let highestNum = group.children().length;

    if(highestNum !== 0) {
        currentIndex = (currentIndex + 1) % highestNum; //if we had the last and click next we want to start with the first one again
    }

    geoJson.removeFrom(mapGermany); //remove old geoJson
    geoJson = L.geoJSON(buildboxChooses[currentIndex], {  //render the next item from the buildbox
        style: style,
        onEachFeature: onEachFeature
    }).addTo(mapGermany);

    chosenInfo.update();
}

function toggleVotersMode(){
    voters_mode = !voters_mode;
    geoJson.resetStyle();

    if(voters_mode){
        $("#voters_mode_trigger_btn").html("Election Mode");
    }
    else{
        $("#voters_mode_trigger_btn").html("Voters Mode")
    }
}

// custom style of each feature (i.e. each wahlkreis)
function style(feature) {

    if(voters_mode){
        return {
            fillColor: "#000000",
            weight: 1,
            opacity: 1,
            color: 'grey',
            dashArray: '3',
            fillOpacity: parseFloat(feature.properties.total_votes) / parseFloat(feature.properties.eligible_voters)
        }

    }
    else{
        let votes_map = new Map([
            ["cdu", feature.properties.union],
            ["spd", feature.properties.spd],
            ["gruene", feature.properties.gruene],
            ["afd", feature.properties.afd],
            ["linke", feature.properties.linke],
            ["fdp", feature.properties.fdp],
            ["misc", feature.properties.misc],
        ]);
        let winning_party = [...votes_map.entries()].reduce((a, e) => parseInt(e[1]) > parseInt(a[1]) ? e : a);
        let color_map = new Map([
            ["cdu", "#000000"],
            ["spd", "#E3000F"],
            ["gruene", "#46962B"],
            ["afd", "#009EE0"],
            ["linke", "#BE3075"],
            ["fdp", "#FFFF00"],
            ["misc", "#808080"],
        ]);

        //calculate percentages
        let numOr0 = n => isNaN(n) ? 0 : n
        let votes = [...votes_map.values()].map(val => parseInt(val));
        let sum = votes.reduce((a,b) => numOr0(a) + numOr0(b), 0); //calculate total amount of votes, use 0 in calculation if summand is not a number
        let percentages = votes.map(val => parseFloat((val / sum * 100).toFixed(2))); //calculate percentage and trim to 2 decimal places
        let percentages_map = new Map([
            ["cdu", percentages[0]],
            ["spd", percentages[1]],
            ["gruene", percentages[2]],
            ["afd", percentages[3]],
            ["linke", percentages[4]],
            ["fdp", percentages[5]],
            ["misc", percentages[6]],
        ]);

        //calculate opacity based on majority
        function dynamicOpacity(percentage){
            if(percentage >= 50){
                return 1; //absolute majority --> full opacity
            }
            else{
                return percentage * 2 / 100; // less than absolute --> maps 50% too 100% opacity and then lowers according to value
            }
        }

        return {
            fillColor: color_map.get(winning_party[0]),
            weight: 1,
            opacity: 1,
            color: 'grey',
            dashArray: '3',
            fillOpacity: dynamicOpacity(percentages_map.get(winning_party[0]))
        }
    }
}

//style change on mouseover
function hightlightOnMouseOver(e){
    let layer = e.target;
    layer.setStyle({
        weight: 5,
        color: 'white',
        dashArray: '',
    });

    layer.bringToFront();

    info.update(layer.feature.properties);
}

//style reset on mouseout
function resetHighlight(e){
    geoJson.resetStyle(e.target);
    info.update(null);
}

//on click jump to the state
function zoomToState(e) {
    mapGermany.fitBounds(e.target.getBounds());
}

//assign listeners
function onEachFeature(feature, layer){
    layer.on({
        mouseover: hightlightOnMouseOver,
        mouseout: resetHighlight,
        click: zoomToState
    });
}

$(document).ready(function(){


    $("[id^=election_select]").on('change', function () {
        $("[id^=year_select]").html($("#year_select_1").find("option").filter('[election_type="' + this.value + '"]'));
    }).trigger('change');

    $("#sortable").sortable();
    $("#sortable").disableSelection();

    //set up the map
    mapGermany = L.map("map_germany").setView([50.9, 10.3], 7);

    //tile layer
    L.tileLayer("https://b.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',

    }).addTo(mapGermany);

    buildboxChooses.push(wahlkreise);
    currentIndex = 0;
    //wahlkreise passed from the server on the first call to the site, needed to init this variable in the html file because of jinja
    geoJson = L.geoJSON(wahlkreise, {
        style: style,
        onEachFeature: onEachFeature
    }).addTo(mapGermany);

    info = L.control();
    info.onAdd = function (map) {
        this._div = L.DomUtil.create('div', 'info_right');
        this.update();
        return this._div;
    };

    // update info window with the data of the hovered state
    info.update = function (properties) {
        let percentages = [];
        if(properties) {
            let votes = [properties.union, properties.spd, properties.gruene, properties.afd, properties.linke, properties.fdp, properties.misc].map(val => parseInt(val)); //parse strings to int
            let numOr0 = n => isNaN(n) ? 0 : n
            let sum = votes.reduce((a,b) => numOr0(a) + numOr0(b), 0); //calculate total amount of votes, use 0 in calculation if summand is not a number
            percentages = votes.map(val => (val / sum * 100).toFixed(2)); //calculate percentage and trim to 2 decimal places
        }
        this._div.innerHTML = '<h4>Wahlergebnisse</h4>' +
            (properties ?
            '<b>' + properties.WKR_NAME + ', ' + properties.LAND_NAME + '</b>' +
            '<table class="faction_table">' +
            '       <tr><td><div class="faction_square cdu"/></td><td>CDU/CSU : </td><td>' + percentages[0] + '%' + '</td></tr>' +
            '       <tr><td><div class="faction_square spd"/></td><td>SPD : </td><td>' + percentages[1] + '%' + '</td></tr>' +
            '       <tr><td><div class="faction_square gruene"/></td><td>GRÜNE : </td><td>' + percentages[2] + '%' + '</td></tr>' +
            '       <tr><td><div class="faction_square afd"/></td><td>AFD : </td><td>' + percentages[3] + '%' + '</td></tr>' +
            '       <tr><td><div class="faction_square linke"/></td><td>LINKE : </td><td>' + percentages[4] + '%' + '</td></tr>' +
            '       <tr><td><div class="faction_square fdp"/></td><td>FDP : </td><td>' + percentages[5] + '%' + '</td></tr>' +
            '       <tr><td><div class="faction_square misc"/></td><td>Sonstige : </td><td>' + percentages[6] + '%' + '</td></tr>' +
            '       <tr><td></td><td>Wahlberechtigte : </td><td>' + properties.eligible_voters + '</td></tr>' +
            '       <tr><td></td><td>abgegebene Stimmen : </td><td>' + properties.total_votes + '</td></tr>' +
            '</table>'
            : 'Hover over a state');
    };

    info.addTo(mapGermany);

    voters_mode_trigger_button = L.control({position: "bottomleft"});
    voters_mode_trigger_button.onAdd = function(map){
        let div = L.DomUtil.create("div", "voters_mode_trigger");
        div.innerHTML = '<div id="voters_mode_trigger_btn" class="btn btn-primary" onclick="toggleVotersMode()">Voters Mode</div>';
        return div;
    }
    voters_mode_trigger_button.addTo(mapGermany);

    prevNext = L.control({position: "bottomright"});
    prevNext.onAdd = function(map){
        let div = L.DomUtil.create("div", "prevNext");
        div.innerHTML = '<div class="btn btn-primary" onclick="renderPrev()">Previous</div><div class="btn btn-primary" onclick="renderNext()">Next</div>'
        return div;
    }
    prevNext.addTo(mapGermany);

    chosenInfo = L.control({position: "topleft"});
    chosenInfo.onAdd = function(map){
        this._div = L.DomUtil.create('div', 'info_left');
        this.update();
        return this._div;
    }
    chosenInfo.update = function(){
        let election_type = "";
        switch(buildboxChooses[currentIndex].parameters.election_type){
            case "btw": {
                election_type = "Bundestagswahl";
                break;
            }
            case "ew": {
                election_type = "Europawahl";
                break;
            }
            case "ltw": {
                election_type = "Landtagswahl";
                break;
            }
            default: {
                election_type = "Wahl";
                break;
            }
        }
        this._div.innerHTML = '<h4> currently rendered: </h4>' +
            election_type + ' ' + buildboxChooses[currentIndex].parameters.election_year
    }
    chosenInfo.addTo(mapGermany);


});