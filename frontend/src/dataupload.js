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
                        let feature1_select = document.getElementById('feature1');
                        let feature2_select = document.getElementById('feature2');
                        output_select.innerHTML = "";
                        column_names.forEach((column_name) => {
                            let option = document.createElement('option');
                            option.value = column_name;
                            option.text = column_name;
                            output_select.appendChild(option);
                            feature1_select.appendChild(option.cloneNode(true));
                            feature2_select.appendChild(option.cloneNode(true));
                        });
                        // select the last item fro output_select
                        output_select.selectedIndex = output_select.length - 1;
                        // select the second element from feature2_select
                        feature2_select.selectedIndex = 1;
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


