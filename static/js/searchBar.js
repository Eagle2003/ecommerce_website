let searchBarAutoComplete = M.Autocomplete.init
(		
    document.getElementById('search-input'),
    {
        data : {
            "google" : null,
            "apple" : null,
            "peachy" : null
        },
        onAutocomplete : () =>{document.getElementById('search-form').submit()}					
    }
    );

//setup before functions
let typingTimer;                //timer identifier
let doneTypingInterval = 500;  //time in ms (5 seconds)
let myInput = document.getElementById('search-input');

// Bind enter key to sumbit form
myInput.addEventListener('keyup', (e)=>{if (e.keyCode == 13) document.getElementById('search-form').submit} )

//on keyup, start the countdown
myInput.addEventListener('keyup', () => {
clearTimeout(typingTimer);
if (myInput.value) {
typingTimer = setTimeout(issueQuickSearch, doneTypingInterval);
}
});

//user is "finished typing," do something
function issueQuickSearch () {
    console.log('hey i am done typing')
    let request = new XMLHttpRequest();
    let url = quickSearchURL+"&search="+myInput.value
    request.open("GET", url);
    request.send()

    request.onreadystatechange= function() {
        if (this.status==200 && this.readyState==4) {
            let keywords = JSON.parse(request.responseText)
            console.log(keywords)
            let data =  Object.fromEntries(keywords.map(key => [key, null] ))
            console.log(keywords)
            // update the auto complete
            searchBarAutoComplete.updateData(data)
            searchBarAutoComplete.open()
        }
    }
}