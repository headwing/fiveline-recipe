$(document).ready(function(){
    show_recipe();
})

function show_recipe(){
    $.ajax({
        type: 'GET',
        url: '/FLR',
        data: {},
        success: function (response) {
            let rows = response['posts']
            for (let i = 0; i < rows.length; i++) {
                let image = rows[i]['image']
                let recipe = rows[i]['recipe']
                let cookingtime = rows[i]['cookingtime']
                let star = rows[i]['star']

                let temp_html = `<div class="col-md-6 col-lg-4 mb-3">
                                    <div class="card">
                                        <div class="card-img">
                                            <img src="${image}" alt="" class="img-fluid w-100">
                                            <div class="mask"></div>
                                        </div>
                                        <div class="card-body">
                                            <h4 class="card-title">${recipe}</h4>
                                            <p class="card-text"></p>
                                            <div class="time">
                                                <i class="far fa-clock"></i> ${cookingtime}
                                            </div>
                                            <div class="star">${star}</div>
                                            <br>
                                            <button class="btn btn-success">MORE</button>
                                        </div>
                                    </div>
                                 </div>`
                $('#card-box').append(temp_html)
            }
        }
    });
}

function logout() {
    token_receive = request.cookies.get('mytoken')
    console.log(token_receive)
    $.removeCookie('mytoken');
    alert('로그아웃!')
    window.location.href = '/login'
}