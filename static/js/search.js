var offset = 0
var loadResult = true
const limit = 20
const productsRow = document.getElementById('productsRow')
const loader = document.getElementById('preloader')


//To add items when user scrools to bottom of the pages
issueRequest()
window.onscroll = function(ev) {
    if ((window.innerHeight + window.scrollY + 1) >= document.body.offsetHeight && loadResult) {
        issueRequest()
    }
};
        


// Issues Reuest to server
function issueRequest() {

    loader.classList.remove('hide')
    const request = new XMLHttpRequest();
    const url = productURL+"&offset="+offset+"&search="+keyword+"&limit="+limit;
    request.open("GET", url);
    request.send()

    request.onreadystatechange= function() {
        if (this.status==200 && this.readyState==4) {
            const products = JSON.parse(request.responseText)
            console.log(products)
            l = Object.keys(products).length;
            if (l == 0) loadResult = false
            offset += l 
            loader.classList.add('hide')
            for (index in products) addProduct(products[index])
            // init the tool tips
                          
            
        }
    }
}

// Add products to server
function addProduct (product) {
    console.log('adding product' + product)
    const innerHtml = `
    <div class="col s6 m3 product-col" >
        <a href="${productPageURL+product['id']}" style="display:block;">
        <div class="card  product-card medium  hoverable"  title="${product['name']}">
            <div class="card-content">
                <div class="row">
                    <div class="col s10 offset-s1" >
                        <img class="responsive-img"  src="${mediaURL+ product['images'][0]}">
                    </div>
                </div>
                <div class="row black-text">
                    <div class="col s12">
                        <p class="truncate  flow-text"> ${product['name']} </p>
                    </div>  
        
                    <div class=" col s12"> 
                        <span style="font-variant: small-caps;"><s>Dhs ${product['list_price']} </s></span>
                        <span class="white-text center-align teal"  style="height:25px;width:60px;border-radius:25px; float:right;" >${product['discount']}% off</span>
                        <h5 class= "flow-text" style="margin-top:5px">Dhs ${product['display_price']}</h5>
                        
                    </div>
                </div>
                
                
            </div>
        </div>
        </a>
    </div>    
    ` 

   
    productsRow.innerHTML += innerHtml
    
}

// To add end of search 
function endOfSearch() {
    console.log("End Of search")
    const innerHTML = `
    
    `
}




