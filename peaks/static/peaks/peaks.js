$(document).ready(function(){
    // Select order
    $("#id_order").change(function(){
        this.form.submit();
    })

    // load map if map div exists
    if ($("#map").length) {
        const mapdiv = document.getElementById('map');
        const lat = parseFloat(mapdiv.dataset.lat);
        const lon = parseFloat(mapdiv.dataset.lon);
        const region = mapdiv.dataset.region;
        const mode = mapdiv.dataset.mode;
        var zoom = 11;

        if (mode === "alps"){
            zoom = 6
        } else if (mode === "region") {
            zoom = 8
        } 

        var map = L.map('map').setView([lat, lon], zoom);

        var osmlayer = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        });

        var terrainlayer = new L.StamenTileLayer("terrain").addTo(map);
        map.addLayer(terrainlayer);

        var baseMaps = {
            "Terrain": terrainlayer,
            "OpenStreetMap": osmlayer
        };

        var overlayMaps = {};

        var layerControl = L.control.layers(baseMaps, overlayMaps).addTo(map);

        // Marker of peak
        if (mode === "peak" | mode === "edittour" | mode == "tour"){
            var marker = L.marker([lat, lon]).addTo(map);
        }
        

        // Add regional peaks
        if (!(region == "None" || mode === "edittour")) {
            $.get(`/json/${region}`, function(data, status){
                
                var gjsonlayer = L.geoJSON(data, {
                    onEachFeature: onEachFeature
                }).addTo(map);
            });
        } 

        // Top peaks of the Alps
        if (!(mode === "edittour")){
            console.log("Fetch top peaks")
            $.get("/json/", function(data, status){
                console.log("Got top peaks")

                const filtered = data.filter(function(jsonObject){
                    return jsonObject.properties.region != region;
                });

                var toppeakleayer = L.geoJSON(filtered, {
                    onEachFeature: onEachFeature2
                }).addTo(map);
            });
        }

        // Tour edit: listen to map click events
        if (mode === "edittour"){
            map.on('click', addWaypoint);
        }

    }

    // get wikimedia data if wiki div exists
    if ($("#wiki").length) {
        // Hide the divs as long as we dont have content
        $('#wikiimgcontainer').hide();
        $('#wiki').hide();

        // Search for title, but make "Mont Blanc - Monte Bianco", "Mont Dolent / Monte Dolent" etc. work
        var title = document.getElementById('wiki').dataset.title;
        if (title.includes("-")){
            title = title.split("-")[0];
            
        } else if (title.includes("/")){
            title = title.split("/")[0];
        }
        title = title.trim();

        // First search for matching articles
        var wikiapi = `https://en.wikipedia.org/w/api.php?action=opensearch&search=${title}&namespace=0&limit=1&format=json`;
        // Does not work with $.get because of Cross-Origin Resource Sharing
        $.ajax({
            url: wikiapi, 
            header: {
                'Access-Control-Allow-Origin' : '*',
                'Content-Type': 'application/json'
            },
            method: 'GET',
            dataType: 'jsonp',
            data: '',
            
            success: function(data){
                // Get extract and image 
                const thumbsize = 400;
                const wikititle = data[1][0];
                // Check if we really got a page as search result
                if (wikititle){
                    wikiapi = `https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts|pageimages|pageterms&pithumbsize=${thumbsize}&exintro&explaintext&redirects=1&titles=${wikititle}`;
                    $.ajax({
                        url: wikiapi,
                        header: {
                            'Access-Control-Allow-Origin' : '*',
                            'Content-Type': 'application/json'
                        },
                        method: 'GET',
                        dataType: 'jsonp',
                        data: '',
                        
                        success: function(data){
                            // I need to get the pageid that is a key in the JSON object
                            var pageid = Object.keys(data.query.pages)[0]
                            $("#wikiextract").text(shortenString(data.query.pages[pageid].extract));
                            $("#wikiextract").append(`<div><a href="https://en.wikipedia.org/wiki/${data.query.pages[pageid].title}">Wikipedia</a></div>`)
                            $("#wikilink").html(`<a href="https://en.wikipedia.org/wiki/${data.query.pages[pageid].title}">${title} on Wikipedia</a>`);
                            $('#wiki').show();
                            if (data.query.pages[pageid].hasOwnProperty('thumbnail')) {
                                const thumbnail = data.query.pages[pageid].thumbnail
                                var s = `<img src="${thumbnail.source}" width="${thumbnail.width}" height="${thumbnail.height} alt="${title}" class="maxwidth"\>`
                                $("#wikiimg").html(s); 

                                $('#wikiimgcontainer').show();
                                // Query for image credits
                                const pageimg = data.query.pages[pageid].pageimage
                                wikiapi = `https://en.wikipedia.org/w/api.php?action=query&prop=imageinfo&iiprop=extmetadata&titles=File:${pageimg}&format=json`;
                                $.ajax({
                                    url: wikiapi, 
                                    header: {
                                        'Access-Control-Allow-Origin' : '*',
                                        'Content-Type': 'application/json'
                                    },
                                    method: 'GET',
                                    dataType: 'jsonp',
                                    data: '',

                                    success: function(data){
                                        // I need to get the pageid that is a key in the JSON object
                                        const pgid = Object.keys(data.query.pages)[0];
                                        const metadata = data.query.pages[pgid].imageinfo[0].extmetadata;
                                        // Strip html from artists (like lists and links)
                                        const artists = metadata.Artist.value.replace(/<[^>]+>/g, '');
                                        // License: Public domain does not have license url
                                        var license = "";
                                        if ("LicenseUrl" in metadata) {
                                            license = `<a href="${metadata.LicenseUrl.value}">${metadata.LicenseShortName.value}</a>`;
                                        } else {
                                            license = metadata.LicenseShortName.value;
                                        }
                                        
                                        s = `<small><i>© <a href="https://commons.wikimedia.org/wiki/File:${pageimg}">${artists} / Wikimedia</a></i>, ${license}</small>`;
                                        $("#wikiimgcred").html(s);
                                    }
                                });
                            }
                        }
                    });
                }    
            }});

            
        }

});


function shortenString(str) {
    const maxwords = 60;
    var shorter = str.split(/\s+/).slice(0, maxwords).join(" ");
    // Only shorten string if it makes sense
    if (shorter.length < str.length - 100){
        shorter = shorter + " ..."
    } else {
        shorter = str;
    }

    return shorter;
}


function onEachFeature(feature, layer) {
    const mountainIcon = L.icon({
        iconUrl: '/static/peaks/mountain.svg',
        iconSize:     [20, 20], 
        iconAnchor:   [10, 10], 
    });

    const mountainIconSmall = L.icon({
        iconUrl: '/static/peaks/mountain.svg',
        iconSize:     [15, 15], 
        iconAnchor:   [7, 7], 
    });

    layer.bindTooltip(feature.properties.name);
    if (feature.properties.neargtdist >= 1) {
        layer.setIcon(mountainIcon);
    } else {
        layer.setIcon(mountainIconSmall);
    }

    layer.on('click', function(e) {
        window.location.href = `/peak/${e.target.feature.properties.slug}`;
    })
    
}

function onEachFeature2(feature, layer) {

    const mountainIconGrey = L.icon({
        iconUrl: '/static/peaks/mountain-grey.svg',
        iconSize:     [15, 15], 
        iconAnchor:   [7, 7], 
    });

    layer.bindTooltip(feature.properties.name);
    layer.setIcon(mountainIconGrey);
  
    layer.on('click', function(e) {
        window.location.href = `/peak/${e.target.feature.properties.slug}`;
    })
    
}

function addWaypoint(e) {
    console.log(e.latlng)
    const lat = e.latlng.lat;
    const lon = e.latlng.lng;
    // Clone the last (still empty) waypoint
    var oldElement = $('.wp:last')
    var newElement = oldElement.clone(true);

    // Set lat lon
    oldElement.find('.latlon').html('<small>' + lat.toFixed(4) + ', ' + lon.toFixed(4) + '</small>');
    oldElement.find("input[name*='lat']").val(lat);
    oldElement.find("input[name*='lon']").val(lon);

    // Update index numbers 
    var total = $('#id_form-TOTAL_FORMS').val();
    oldElement.find("input[name*='number']").val(total);
    newElement.find(':input').each(function() {
        var name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('');
    });
    
    // Update management form and wp number
    total++;
    $('#id_form-TOTAL_FORMS').val(total);
    newElement.find('.wpnumber').text(`${total}`);

    // Insert new form
    oldElement.after(newElement);



    
}