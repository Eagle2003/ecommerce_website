
    // basic Valdiations
    function data_required(value) {
        if (value == '' ) throw Error("Field is empty")

    }

    // String Validations
    function _length_required(value, min=null, max=null){
        if (min == max && min && value.length != max) {
            if (value.length != min) throw Error(`Field should be exactly ${min} long`)
        }else if (min && max && (value.length < min || value.length > max) ){
            throw Error(`Input should be between ${min}-${max} charcters long`)
        }
        else if (min && value.length < min) {
            throw Error(`Input Should be atleast ${min} long `)
        }else if (max && value.length > max ){
            throw Error(`Input can be only ${max} characters long`)
        }
    }

    function length_required(min=null, max=null) {
        console.log(min, max)
        return (value) => _length_required(value, min=min, max=max)
    }

    function number_required(value) {
        if (!value.match(/^\d+$/)) throw Error("Invalid input only numbers allowed !")
    }

    // Integer Validations
    function _integer_between(value, min, max){
        value = parseInt(value)
        if (!value && value != 0) throw Error("Only Numbers Allowed")
        if (value < min && min) throw Error(`Input should be greater than  ${min}`)
        else if (value > max && max) throw Error (`Input should be smaller than ${max}`)
    }

    function integer_between(min, max){
        return (value) => _integer_between(value, min=min, max=max)
        
    }

    // Float Validations
    function _float_between(value, min, max) {
        value = parseFloat(value)
        console.log(value)
        if (! value) throw Error('Input is can only contain numbers')
        if (value < min) throw Error(`Input should be greater than  ${min}`)
        else if (value > max) throw Error (`Input should be smaller than ${max}`)
    }

    function float_between (min, max){
        return (value) => _float_between(value, min, max)
    }


    // File Validation Functions
    function _valid_files_only(value, field, valid_file_types){
        for (var i=0; i<field.files.length; i++){
            if (! valid_file_types.includes(field.files[i].type) ) throw Error(`Invalid File Type`)
        }
    }

    function valid_file_type(valid_file_types) {
        return (value, field)=>{_valid_files_only(value, field, valid_file_types)}
    }

    function _number_of_files (value, field, min, max){
        if (field.files.length > max )throw Error(`Max File Limit : ${max}`)
        if (field.files.length < min )throw Error(`Min Number Of File : ${min}`)
    }

    function number_of_files (min, max) {
        return (value, field) => _number_of_files(value, field, min, max)
    }

    function validateForm(form) {
        validated  = true
        for (field_id in form){
            field = document.getElementById(field_id) 
            console.log(field_id)
            console.log(form[field_id])
            error = document.getElementById(field_id+"_error")
            if ((!form[field_id].includes(data_required)) && field.value =='')  {
                console.log('value empty adn accepted')
                continue}
            for (i in form[field_id]) {
                error.innerHTML = ''
                field.classList.remove('invalid')
                try {
                    form[field_id][i](field.value, field)
                }catch (err) {
                    console.log("error found")
                    validated = false
                    field.classList.add('invalid')
                    error.innerHTML = err.message
                    break            
                }

            }
        }

        return validated
    }
