var apigClient = apigClientFactory.newClient();
window.SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition
// var image='/Users/sakshatkatyarmal/Downloads/IMG_1410.jpg';
function voiceSearch(){
    if ('SpeechRecognition' in window) {
        console.log("SpeechRecognition is Working");
    } else {
        console.log("SpeechRecognition is Not Working");
    }
    
    var inputSearchQuery = document.getElementById("search_query");
    const recognition = new window.SpeechRecognition();
    //recognition.continuous = true;

    micButton = document.getElementById("mic_search");  
    
    if (micButton.innerHTML == "mic") {
        recognition.start();
    } else if (micButton.innerHTML == "mic_off"){
        recognition.stop();
    }

    recognition.addEventListener("start", function() {
        micButton.innerHTML = "mic_off";
        console.log("Recording.....");
    });

    recognition.addEventListener("end", function() {
        console.log("Stopping recording.");
        micButton.innerHTML = "mic";
    });

    recognition.addEventListener("result", resultOfSpeechRecognition);
    function resultOfSpeechRecognition(event) {
        const current = event.resultIndex;
        transcript = event.results[current][0].transcript;
        inputSearchQuery.value = transcript;
        console.log("transcript : ", transcript)
    }
}


function textSearch() {
    var searchText = document.getElementById('search_query');
    if (!searchText.value) {
        alert('Please enter a valid text or voice input!');
    } else {
        searchText = searchText.value.trim().toLowerCase();
        console.log('Searching Photos....');
        searchPhotos(searchText);
    }
    
}

function searchPhotos(searchText) {

    console.log(searchText);
    document.getElementById('search_query').value = searchText;
    document.getElementById('photos_search_results').innerHTML = "<h4 style=\"text-align:center\">";

    var params = {
        'q' : searchText
    };
    var additionalParams = {
        headers: {
            
            'x-api-key': '1yqF9nnQSS3JMtcrClWfX83MgXzzRZBJ4I69wb3q'
        }
    }
    
    apigClient.searchGet(params, {}, additionalParams)
        .then(function(result) {
            console.log("Result : ", result);

            // results = result["data"]["body"]["results"];
            results=result.data;
            lor=results.length;
            // console.log("results : ", results);
            console.log(results);
            var photosDiv = document.getElementById("image-display");
            // photosDiv.innerHTML = "";
            if(lor==0){
                photosDiv.innerHTML = '<h2 style="text-align: center;font-size: 25px;font-style: bold;margin-top:30px;">No Images Found !!!</h2>';
            }
            else {

                photosDiv.innerHTML = '<h2 style="text-align: center;font-size: 25px;font-style: bold;margin-top:30px;margin-bottom:30px;">Here are your images: </h2>';
          
                image_paths = result["data"];
                console.log(image_paths);
                  console.log(photosDiv);
                  for (n = 0; n < image_paths.length; n++) {
                      images_list = image_paths[n].split('/');
                      imageName = images_list[images_list.length - 1];
                      photosDiv.innerHTML += '<figure><img src="' + image_paths[n] + '" style="width:25%"><figcaption>' + imageName + '</figcaption></figure>';
          
                   } 
                  
                  console.log(photosDiv);
              }
            
            // for (n = 0; n < results.length; n++) {
            //     url_split = results[n].url.split('/');
            //     imageName = url_split[url_split.length - 1];

            //     photosDiv.innerHTML += '<figure style="display: inline-block"><img src="' + results[n].url + '" style="width:100%"><figcaption>' + imageName + '</figcaption></figure>';
            // }

        }).catch(function(result) {
            console.log(result);
        });
}

function uploadPhoto() {
    var filePath = (document.getElementById('uploaded_file').value).split("\\");
    var fileName = filePath[filePath.length - 1];
    
    var customLabels = document.getElementById('custom_labels');
    if (!customLabels.innerText == "") {
    }
    console.log(fileName);
    console.log(customLabels.value);

    var reader = new FileReader();
    var file = document.getElementById('uploaded_file').files[0];
    console.log('File : ', file);
    document.getElementById('uploaded_file').value = "";
    fileExt = filePath[2].split(".")[1]

    if ((filePath == "") || (!['png', 'jpg', 'jpeg'].includes(filePath[2].split(".")[1]))) {
        alert("Please upload a valid .png/.jpg/.jpeg file!");
    } else {

        var params = {
            'x-amz-meta-customLabels': customLabels.value,
            'bucket': 'photo-sk9428',
            'key': filePath[2]
        };
        var additionalParams = {
            headers: {
                'Access-Control-Allow-Origin': '*',
                'x-api-key': '1yqF9nnQSS3JMtcrClWfX83MgXzzRZBJ4I69wb3q'
            }
        };
  
    
        reader.readAsArrayBuffer(file);
        reader.onload = function (event) {

            console.log("Reader Object",event.target.result)
            console.log("Reader ",reader.result)

            var myHeaders = new Headers();
            myHeaders.append("x-amz-meta-customLabels",  params['x-amz-meta-customLabels']);
            myHeaders.append("Content-Type", "image/jpeg");
            console.log("myHeaders ",myHeaders)
            var file = new Uint8Array(reader.result);
    
            var requestOptions = {
            method: 'PUT',
            headers: myHeaders,
            body: file,
            redirect: 'follow'
            };

            console.log("requestOptions ",requestOptions);

    
            fetch(`https://be290397i6.execute-api.us-east-1.amazonaws.com/first_test/photo-sk9428/${filePath[2]}`, requestOptions)
            .then(response => response.text())
            .then(result => console.log(result)).then(alert("Photo uploaded successfully!"))
            .catch(error => console.log('error', error));

            
            
        }

        // return apigClient.uploadBucketKeyPut(params, new Uint8Array(reader.result), additionalParams)
        //     .then(function(result) {
        //         console.log(result);
        //         alert("Photo uploaded successfully!");
        //     })
        //     .catch(function(error) {
        //         console.log(error);
        //     })




        
    }
}