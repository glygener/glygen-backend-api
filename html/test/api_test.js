var htmlRoot = "";
var titleClass = "prd_api_title";
var serverDomain = "https://api.glygen.org"
var fullUrl = '';

////////////////////////////////////
function getAutomatedCn(testInfo, apiList){
   
    if (window.location.href.indexOf("dev") != -1){
        titleClass = "dev_api_title";    
        serverDomain = "https://api.dev.glygen.org";
    }
    else if (window.location.href.indexOf("tst") != -1){
        titleClass = "tst_api_title";
        serverDomain = "https://api.tst.glygen.org";
    }
    else if (window.location.href.indexOf("beta") != -1){
        titleClass = "beta_api_title";
        serverDomain = "https://beta-api.glygen.org"
    }

    var cn = '';
    for (var j in apiList){
        var k = apiList[j];
        var obj = testInfo[k];
        var tdCls = k + ' regular';

        var fTypeDict = {"string_fields":"", "numeric_fields":"", "object_fields":"", 
            "required_fields":""};
        var st = "width:100%;height:50px;background:#eee;";
        for (var fType in fTypeDict){
            if (fType in obj){
                var val = JSON.stringify(obj[fType]);
                fTypeDict[fType] = '<textarea style="'+st+'">'+ val + '</textarea>';
            }
        }
        
        var qJsonList = [];
        var qLabelList = [];
        if ("query" in obj){
            qLabelList.push("example query");
            qJsonList.push(JSON.stringify(obj["query"]));
        }
        if ("querylist" in obj){
            for (var j in obj["querylist"]){ 
                qJsonList.push(JSON.stringify(obj["querylist"][j]["query"],null, 2));
                qLabelList.push(obj["querylist"][j]["label"]);
            }
        }
        var title = 'Test for ' + k + ' API';
        
        
        cn += '<tr><th colspan=2 align=left class='+titleClass+'>'+title+'</th></tr>';
        
        for (var fType in fTypeDict){
            if (fType in obj){
                var val = fTypeDict[fType];
                cn += '<tr><td valign=top>'+fType+'</td><td width=80% class="'+tdCls+'">'+val+'</td></tr>';
            }
        }
        
        var qId = k + '_queryselector';
        var qSelector = '<select class=qselector id="'+qId+'" style="width:100%;margin-bottom:3px;height:30px;background:#D6EAF8;">';
        for (var i in qJsonList){
            qSelector += "<option value='"+qJsonList[i]+"'>"+qLabelList[i]+"</option>";
        }
        qSelector += '</select>';
        cn += '<tr><td valign=top>Query Examples</td><td width=80% class="'+tdCls+'">'+qSelector+'<br>';
        var s = 'width:100%;height:100px;background:#fff;';
        var qId = k + '_query';
        cn += '<textarea class="'+tdCls+'" id="'+qId+'" style="'+s+'">'+qJsonList[0]+'</textarea></td></tr>';
        cn += '<tr><td>Post Data</td><td id='+k+'_req_cn "></td></tr>';
        var btn = '<input type=submit class=submitbtn id='+k+' name=btn value="Submit API request">';
        var s = 'position:relative;width:900px;height:200px;background:#fff;border:1px solid #ccc;';
        s += 'overflow:auto;';
        var resBox = '<div id='+k+'_res_cn style="'+s+'"></div>';
        cn += '<tr height=100><td valign=top>'+btn+'</td><td>'+resBox+'</td></tr>';
    }

    return cn;
}


////////////////////////////////////
$(document).on('click', '.submitbtn', function (event) {
    event.preventDefault();
    var apiName = this.id;
    var reqCnJqId = '#' + apiName + '_req_cn';
    var resCnJqId = '#' + apiName + '_res_cn';
    var jqClass = '.' + apiName;

    var gifImage = '<img src=loading.gif style="width:20%;margin-left:40%;margin-top:2%;">';
    $(resCnJqId).html(gifImage);
    

    var q = $('#' + apiName + '_query').val();
    var url = testInfo[apiName]["url"];
    if("semantic" in testInfo[apiName]){
        url +=  '/' + q.replace("\"", "").replace("\"", "") + '/';
        var reqObj = new XMLHttpRequest();
        reqObj.open("POST", url, true);
        reqObj.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        reqObj.resCnJqId = resCnJqId;
        reqObj.onreadystatechange = function() {
            if (reqObj.readyState == 4 && [200, 500].indexOf(reqObj.status) != -1) {
                $(this.resCnJqId).html('<pre>' + reqObj.responseText + '</pre>' );
            }
            else{
                console.log(reqObj.responseText);
            }
        };
        reqObj.send();
        fullUrl = serverDomain + '/' + url;
        var urlCn = '<a href="'+fullUrl+'">' + fullUrl + '</a>';
        $(reqCnJqId).html(urlCn);
    }
    else{
        var reqObj = new XMLHttpRequest();
        reqObj.open("POST", url, true);
        var postData = "query=" + JSON.stringify(JSON.parse(q));
        if (url == "/job/addnew"){
            postData = {"query":JSON.parse(q)};
            reqObj.setRequestHeader('Content-Type', 'application/json');
        }
        else{
            reqObj.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        }
        reqObj.resCnJqId = resCnJqId;
        reqObj.onreadystatechange = function() {
            if (reqObj.readyState == 4 && [200, 500].indexOf(reqObj.status) != -1) {
                console.log(reqObj.responseText);
                $(this.resCnJqId).html('<pre>' + reqObj.responseText + '</pre>' );
            }
            else{
                console.log(reqObj.responseText);
            }
        };
        if (url == "/job/addnew"){
            reqObj.send(JSON.stringify(postData));
            fullUrl = serverDomain + '/' + url;
        }
        else{
            reqObj.send(postData);
            fullUrl = serverDomain + '/' + url + '?query=' + JSON.stringify(JSON.parse(q));
        }
        var urlCn = '<a class=fullurl href="'+fullUrl+'" target=_>' + fullUrl + '</a>';
        $(reqCnJqId).html(urlCn);
        console.log(url + '?' + postData);
    }

});

////////////////////////////////////
$(document).on('change', '.qselector', function (event) {
    event.preventDefault();
    var apiName = this.id.replace("_queryselector", "");
    var q = $('#' + apiName + '_queryselector').val();
    $('#' + apiName + '_query').val(q);
});


////////////////////////////////////
$(document).on('click', '.fullurl', function (event) {
    event.preventDefault();
    window.location = fullUrl;
});




