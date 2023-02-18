// global variables
var map; 
const markers = [];

$(document).ready(function(){
    // Select order
    $("#id_order").change(function(){
        this.form.submit();
    })

    // Delete Tour button
    $(".deletetourbtn").click(function(){
        const id = $(this).attr("value");
        $.ajax({
            url: `/tour/${id}`,
            headers: {"X-CSRFToken": CSRF_TOKEN }, 
            type: 'DELETE',
            success: function(result) {
                console.log(result);
            }
        });
    });


    // load map if map div exists
    if ($("#map").length) {
        const mapdiv = document.getElementById('map');
        const lat = parseFloat(mapdiv.dataset.lat);
        const lon = parseFloat(mapdiv.dataset.lon);
        const region = mapdiv.dataset.region;
        const mode = mapdiv.dataset.mode;
        const tour = mapdiv.dataset.tour;
        var zoom = 11;

        if (mode === "alps"){
            zoom = 6
        } else if (mode === "region") {
            zoom = 8
        } 

        map = L.map('map').setView([lat, lon], zoom);

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
        if (!(mode === "tour" || mode === "edittour")){
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

        // Tour: show waypoint markers
        if (mode === "tour"){
            $.get(`/waypoints/${tour}`, function(data, status){             
                var gjsonlayer = L.geoJSON(data, {
                    onEachFeature: onEachWaypoint
                }).addTo(map);
            });
        }

        // Tour edit 
        if (mode === "edittour"){
            // Get existing waypoints
            if (tour){
                $.get(`/waypoints/${tour}`, function(data, status){             
                    var gjsonlayer = L.geoJSON(data, {
                        onEachFeature: onEachWaypointDragable
                    }).addTo(map);
                });
            }
            
            // listen to map click events
            map.on('click', addWaypoint);

            // init nr and lat, lon in the table
            $(".wp").each(function(index) {
                // Get data
                const lat = parseFloat($(this).find("input[name*='lat']").val());
                const lon = parseFloat($(this).find("input[name*='lon']").val());

                // Write data if lat, lon are defined
                if (!isNaN(lat)){
                    $(this).find(".wpnumber").text(`${index + 1}`);
                    $(this).find('.latlon').html('<small>' + lat.toFixed(4) + ', ' + lon.toFixed(4) + '</small>');
                }

            });

            // Delete WP button
            console.log($('#id_form-TOTAL_FORMS').val())
            if ($('#id_form-TOTAL_FORMS').val() > 1){
                $("#deletewpbtn").prop('disabled', false);
            }

            $("#deletewpbtn").click(function(){
                const m = markers.pop()

                if (m != undefined){
                    // remove marker
                    m.remove()
                    
                    // Remove last (empty) WP from table
                    $('.wp:last').remove()

                    // Update total
                    const total = $('#id_form-TOTAL_FORMS').val();
                    $('#id_form-TOTAL_FORMS').val(total - 1);

                    // Clear last (non empty) WP
                    $('.wp:last').find('.latlon').text('Click on map');
                    $('.wp:last').find("input[name*='lat']").val("");
                    $('.wp:last').find("input[name*='lon']").val("");
                    $('.wp:last').find("input[name*='name']").val("");
                    $('.wp:last').find('.wpnumber').text("New");

                    // Evtually disable delete button
                    if ($('#id_form-TOTAL_FORMS').val() <= 1){
                        $("#deletewpbtn").prop('disabled', true);
                    }

                } 


                
            });
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

// Based on http://blog.charliecroom.com/index.php/web/numbered-markers-in-leaflet

L.NumberedDivIcon = L.Icon.extend({
    options: {
    iconUrl: '/static/peaks/wpmarker.png',
    number: '',
    shadowUrl: null,
    iconSize: new L.Point(25, 41),
    iconAnchor: new L.Point(13, 41),
    popupAnchor: new L.Point(0, -33),
    className: 'leaflet-div-icon'
    },
    
    createIcon: function () {
    var div = document.createElement('div');
    var img = this._createImg(this.options['iconUrl']);
    var numdiv = document.createElement('div');
    numdiv.setAttribute ( "class", "number" );
    numdiv.innerHTML = this.options['number'] || '';
    div.appendChild ( img );
    div.appendChild ( numdiv );
    this._setIconStyles(div, 'icon');
    return div;
    },
    
    createShadow: function () {
    return null;
    }
    });


function onEachWaypoint(feature, layer) {
    if (feature.properties.name) {
        layer.bindTooltip(feature.properties.name);
    }
    var icon = new L.NumberedDivIcon({number: `${feature.properties.number}`})
    layer.setIcon(icon);
}

function onEachWaypointDragable(feature, layer) {
    var icon = new L.NumberedDivIcon({number: `${feature.properties.number}`})
    layer.setIcon(icon);

    // Listen to drag events
    layer.options.draggable = true;
    layer.on('dragend', function(e) {
        var latlng = layer.getLatLng();
        console.log(`dragged WP ${feature.properties.number} to ${latlng}`);
        draggedWaypoint(feature.properties.number, latlng);
    })

    markers.push(layer);
 }

function draggedWaypoint(n, latlng){
    // find the n-th row in the table and update lat lon
    var row = $('.wp').eq(n - 1);
    row.find('.latlon').html('<small>' + latlng.lat.toFixed(4) + ', ' + latlng.lng.toFixed(4) + '</small>');
    row.find("input[name*='lat']").val(latlng.lat);
    row.find("input[name*='lon']").val(latlng.lng);
}


function addWaypoint(e) {
    console.log(`new wp ${e.latlng}`)
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
    oldElement.find('.wpnumber').text(`${total}`);
    newElement.find(':input').each(function() {
        var name = $(this).attr('name').replace('-' + (total-1) + '-','-' + total + '-');
        var id = 'id_' + name;
        $(this).attr({'name': name, 'id': id}).val('');
    });
    
    // Show marker
    marker = new L.Marker(e.latlng, {
        draggable: true,
        icon: new L.NumberedDivIcon({number: `${total}`})
        }).addTo(map);
    
    marker.on("dragend", function(e){
        var latlng = e.target.getLatLng();
        draggedWaypoint(total - 1, latlng);
    });

    markers.push(marker);

    
    // Update management form 
    total++;
    $('#id_form-TOTAL_FORMS').val(total);
    

    // Insert new form
    oldElement.after(newElement);

    // Enable delete button
    $("#deletewpbtn").prop('disabled', false);
}