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
                console.log(data.message);
                if(data.hasOwnProperty('success'))
                {
                    if(data.success)
                    {
                        Toastify({
                            text: data.message,
                            duration: 3000
                        }).showToast();
                        $('#datasetviewer').fadeIn(300);
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


