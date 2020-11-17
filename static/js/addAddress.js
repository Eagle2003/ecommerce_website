document.addEventListener('DOMContentLoaded', function() {
    document.getElementsByTagName('main')[0].innerHTML +=`
<!-- Modal to add a address  -->
<div id="add-address" class="modal modal-fixed-footer">
  <form id="address_form" method="POST" action="${addAddressRedirect}">
    ${hidden_tag}
    <!-- Header  -->
    <div class="modal-content">
      <div class="row">
        <div class="col s12">
          <h4 class="teal-text" style="font-weight: 500;" >Add an Adress</h4>

        </div>
      </div>

    
    
    <!-- Adress name and phone -->
    <div class="row">
      <div class="col s12"  >
        <div class="row">
          <div class="input-field col s12 m6">
            <i class="material-icons prefix">account_circle</i>
            <input class="validate" id="address_name" name="name" required type="text" value="">
            <label for="address_name">Address Name</label>
            <span id="address_name_error" class="red-text"></span>


          </div>
          <div class="input-field col s12 m6">
            <i class="material-icons prefix">phone</i>
            <input class="validate" data-length="10" id="address_phone" name="phone"  type="tel" data-length="10" required>
            <label for="address_phone">Conctact number</label>
            <span id="address_phone_error" class="red-text"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Adress row 2 -->
    <div class="row">
      <div class="col s1">
        <i class="material-icons small" style="margin-top: 40%;">map</i>
      </div>
      <!-- Adrees line1 (Basically an emirate)  -->
      <div class="input-field col s11 m5">
        <select id="address_line1" name="line1" class='validate'>
          <option value="" disabled >Choose Your Emirate</option>
          <option value="Abu Dhabi">Abu Dhabi</option>
          <option value="Dubai">Dubai</option>
          <option value="Ajman">Ajman</option>
          <option value="Fujarirah">Fujarirah</option>
          <option value="Ras Al Kaimah">Ras Al Kaimah</option>
          <option value="Sharjah">Sharjah</option>
          <option value="Umm Al Quwain">Umm Al Quwain</option>
        </select>
        <label>Select Your Emirate</label>
        <span id="address_line1_error" class="red-text"></span>
      </div>

      <!-- Adress Line 2 Street Adress -->
      <div class="input-field col s12  m6 ">
        <i class="material-icons prefix">directions</i>
        <input class="validate" id="address_line2" name="line2" required type="text" value="">
        <label class="active" for="address_line2">Street Adress</label>
        <span id="address_line2_error" class="red-text"></span>
      </div>
    </div>

    <!-- Adress Row 3 -->
    <div class="row">
      <!-- Adress line3 Buidling Name and Falt no. -->
      <div class="input-field col s12  ">
        <i class="material-icons prefix">home</i>
        <input class="validate" id="address_line3" name="line3" required type="text" value="">
        <label class="active" for="address_line3">Building Name, Apartment No.</label>
        <span id="address_line3_error" class="red-text"></span>
      </div>  
    </div>

    </div>

    <div class="modal-footer">
      <a href="#!" class="modal-close waves-effect waves-green btn-flat">Cancel</a>
      <button href="#!" type="button" onclick="addAddress()" class=" waves-effect waves-green btn-flat">Submit</button>
      
    </div>
  </form>
</div>

</div>
`})



function addAddress() {

  fields = {
      "address_name" :  [data_required, length_required(null, 20)],
      "address_phone" : [data_required, number_required, length_required(min=8, max=9)],
      "address_line1" : [data_required, length_required(null, 40)],
      "address_line2" : [data_required, length_required(null, 40)],
      "address_line3" : [data_required, length_required(null, 40)]

  }
  
  if (validateForm(fields)) {
    document.getElementById('address_form').submit()

  }
};