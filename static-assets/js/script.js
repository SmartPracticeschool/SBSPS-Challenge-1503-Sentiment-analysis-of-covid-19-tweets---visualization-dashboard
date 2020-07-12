function mapSetting(country) {
    require([
        "esri/Map",
        "esri/views/MapView",
        "esri/symbols/SimpleMarkerSymbol",
        "esri/Graphic",
        "esri/layers/GraphicsLayer"
      ], function(Map, MapView, SimpleMarkerSymbol, Graphic, GraphicsLayer) {
    
      var map = new Map({
        basemap: "dark-gray-vector"
      });
    
      var view = new MapView({
        container: "viewDiv",
        map: map,
        center: [78.9629, 20.5937], 
        zoom: 3
      });
    
      var symbol = {
        type: "simple-marker",  
        style: "circle",
        color: [ 0, 255, 0 , 0.3],
        size: "12px",  
        outline: {  
          color: [ 66, 219, 42 ],
          width: 0  
        }
      };

        var positive = [ 0, 255, 0 , 0.3];
        var negative = [219, 66, 42, 0.8];
        var neutral = [112, 112, 112, 0.5];

        var graphicsLayer = new GraphicsLayer();
        map.add(graphicsLayer);

        for(key in country) {
            var point = {
                type: "point",
                longitude: country[key]['longitude'],
                latitude: country[key]['latitude']
            };
            if(country[key]['positive'] > 0) {
                symbol.color = positive;
                symbol.size = 12 * country[key]['positive'];
                var pointGraphic = new Graphic({ 
                    geometry: point, 
                    symbol: symbol 
                });
                graphicsLayer.add(pointGraphic);
            }
            if(country[key]['neutral'] > 0) {
                symbol.color = neutral;
                symbol.size = 12 * country[key]['neutral'];
                var pointGraphic = new Graphic({ 
                    geometry: point, 
                    symbol: symbol 
                });
                graphicsLayer.add(pointGraphic);
            }
            if(country[key]['negative'] > 0) {
                symbol.color = negative;
                symbol.size = 12 * country[key]['negative'];
                var pointGraphic = new Graphic({ 
                    geometry: point, 
                    symbol: symbol 
                });
                graphicsLayer.add(pointGraphic);
            }
        }
        console.log(graphicsLayer.loadStatus);
    });
}

var ids = ['positive-container', 'neutral-container', 'negative-container'];
function show(country, id) {
    fillContent(country, id.split("-")[0]);
    document.getElementById(id).style.visibility = "visible";
    for(var i = 0; i < ids.length; i++)
    {
        if(ids[i] != id) {
            document.getElementById(ids[i]).style.visibility = "hidden";
        }
    }
}

function fillContent(country, situation) {
    var left = document.getElementById("left");
    var right = document.getElementById("content");

    var positive = "#4CD851"
    var neutral = "#707070";
    var negative = "#EC4949";
    var color = "";

    if(situation == "positive")
        color = positive;
    else if(situation == "neutral")
        color = neutral;
    else
        color = negative;

    var contentLeft = "<span style='color : "+color+"; font-weight:bolder; displaye: inline'>"+situation +" tweets places</span>";
    var contentRight = "";

    for(key in country) {
       if (country[key][situation] > 0){
        contentLeft += "<br/>" + key;
       }
       contentRight += "<span style='display: block; text-align: center; width: 100%; background-color: #333333; border-bottom: 1px solid #e6e6e6; border-top:1px solid #e6e6e6;'>"+ key +"</span><br/><span style='color:"+positive+"'>Positive : </span>"+ country[key]['positive'] + "</span><br/><span style='color:"+neutral+"'>Neutral : </span>"+ country[key]['neutral'] + "</span><br/><span style='color:"+negative+"'>Negative : </span>"+ country[key]['negative'] + "<br/>";
    }
    
    left.innerHTML = contentLeft;
    right.innerHTML = contentRight;
}

function wordcloud(positive, negative, neutral, country) {

    fillContent(country, 'positive');
    var entries = [];
    for(index = 0; index < positive.length; index++) {
        entries.push({label : positive[index], url:'#', target:'_top'});
    }

    console.log(entries);

    var settings1 = {
        entries : entries,
        width : 640,
        height : 180,
        radius : '65%',
        radiusMin : 75,
        bgDraw : true,
        brColor : "#292929",
        opacityOver : 1.00,
        opacityOut : 0.05,
        opacitySpeed : 6,
        fov : 800,
        speed : 2,
        fontFamily : 'Courier, Arial, sans-serif',
        fontSize : '30',
        fontColor : "#4CD851",
        fontWeight : 'bold',
        fontstyle : 'normal',
        fontSretch : 'normal',
        fontToUppercase : true
    };

    let settings2 = {...settings1};
    let settings3 = {...settings1};

    entries = []
    for(index = 0; index < neutral.length; index++) {
        entries.push({label : neutral[index], url:'#', target:'_top'});
    }
    settings2.entries = entries;
    
    entries = []
    for(index = 0; index < negative.length; index++) {
        entries.push({label : negative[index], url: '#', target:'_top'});
    }
    settings3.entries = entries;
    settings2.fontColor = "#707070";
    settings3.fontColor = "#EC4949";

    console.log(settings1);
    console.log(settings2);
    console.log(settings3);

    $('#positive-container').svg3DTagCloud(settings1);
    $('#neutral-container').svg3DTagCloud(settings2);
    $('#negative-container').svg3DTagCloud(settings3);
}
