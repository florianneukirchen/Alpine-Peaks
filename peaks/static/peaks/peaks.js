$(document).ready(function(){
    // load map if map div exists
    if ($("#map").length) {
        const mapdiv = document.getElementById('map');
        const lat = parseFloat(mapdiv.dataset.lat);
        const lon = parseFloat(mapdiv.dataset.lon);

        var map = L.map('map').setView([lat, lon], 13);

        var osmlayer = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);

        var terrainlayer = new L.StamenTileLayer("terrain");
        map.addLayer(terrainlayer);

        var baseMaps = {
            "Terrain": terrainlayer,
            "OpenStreetMap": osmlayer
        };

        var overlayMaps = {};

        var layerControl = L.control.layers(baseMaps, overlayMaps).addTo(map);

        var marker = L.marker([lat, lon]).addTo(map);
    }

    // get wikimedia data if wiki div exists
    if ($("#wiki").length) {
        // First search for matching articles
        const title = document.getElementById('wiki').dataset.title;
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
                            if (data.query.pages[pageid].hasOwnProperty('thumbnail')) {
                                const thumbnail = data.query.pages[pageid].thumbnail
                                var s = `<img src="${thumbnail.source}" width="${thumbnail.width}" height="${thumbnail.height} alt="${title}"\>`
                                $("#wikiimg").html(s); 
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
                                        s = `<small><i>© <a href="https://commons.wikimedia.org/wiki/File:${pageimg}">${metadata.Artist.value} / Wikimedia</a></i>, <a href="${metadata.LicenseUrl.value}">${metadata.LicenseShortName.value}</a></small>`;
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