const form = document.getElementById('upload-form');
form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    $.ajax({
        url: 'http://127.0.0.1:1407/dataset',
        type: 'post',
        data:formData,
        contentType: false,
        cache: false,
        processData: false,
        success:function(data){
            if(data.hasOwnProperty('message'))
            {
                Toastify({
                    text: data.message,
                    duration: 3000
                }).showToast();
                console.log(data.message);
                if(data.hasOwnProperty('success'))
                {
                    if(data.success)
                    {
                        
                        $('#datasetviewer').fadeIn(300);

                        // append the column names to output-select id dropdown
                        let column_names = data.columns;
                        let output_select = document.getElementById('output-select');
                        
                        output_select.innerHTML = "";
                        let filter_div = document.getElementById('filter_checkboxes');
                        $("#filter_message").text("Select the columns to be filtered");
                        column_names.forEach((column_name) => {
                            let option = document.createElement('option');
                            option.value = column_name;
                            option.text = column_name;
                            output_select.appendChild(option);
                            
                            let filter_checkbox = document.createElement('input');
                            filter_checkbox.type = "checkbox";
                            filter_checkbox.name = column_name;
                            filter_checkbox.value = column_name;
                            filter_checkbox.checked = true;
                            filter_checkbox.className = "filter-checkbox";
                            filter_div.appendChild(filter_checkbox);
                            let filter_label = document.createElement('label');
                            filter_label.for = column_name;
                            filter_label.innerHTML = column_name;
                            filter_label.className = "filter-label";
                            filter_div.appendChild(filter_label);
                            let br = document.createElement('br');
                            filter_div.appendChild(br);

                        });
                        // select the last item fro output_select
                        output_select.selectedIndex = output_select.length - 1;
                        
                        $('#modelparams').fadeIn(300);
                    }
                }
                

            }
        },
        error: function(jqXHR, exception){
            if (jqXHR.status === 0) console.log("Could not connect to server");
            else if (jqXHR.status == 404) console.log("Backend not working");
            else if (jqXHR.status == 500) console.log("Server Error");
            $("#modelloading").hide();
        },
    });
});


