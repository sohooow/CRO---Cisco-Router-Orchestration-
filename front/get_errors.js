async function getErrors(url) {
    try {
        let res = await fetch(url);
        return await res.json();
    } 
    catch (error) {
        console.log(error);
    }
}

async function getLastError() {
    let url = '/last-errors';
    return getErrors(url)
}

async function getNewError() {
    let url = '/get-errors';
    return getErrors(url)
}


function getBigDescriptionHtml(error) {
    if (!getBigDescriptionHtml.hasOwnProperty('count'))
        getBigDescriptionHtml.count = 0;
    getBigDescriptionHtml.count++;
    $(document).ready(function(){
        $('.modal').modal();
    })
    let description = `<div id="m" class="row">
                            <div class="col s12">
                                    ${error.description.substr(0, 50)}
                                <a id="popup" class="modal-trigger inline bold" href="#modal${getBigDescriptionHtml.count}" >...</a>
                                <div id="modal${getBigDescriptionHtml.count}" class="modal">
                                    <div class="modal-content">
                                        <p>${error.description}</p>
                                    </div>
                                </div>
                            </div>                
                        </div>
                    `;
    return description;
}

function getSmallDescriptionHtml(error){
    let description = `<div>${error.description}</div>`;
    return description;
}

function getHtmlErrors(nbr_errors,errors,environment) {
            let html = '<div class="col m5 s12 border">'
            errors.error_log[environment].forEach((error, index) => {
                html += `<div class="row vertical-align-url"><a href="${error.address}/swagger" class="url">${error.address}</a></div>`
                if (index < nbr_errors-1)
                    html += '<hr>'
            })
            html += '</div>'

            html += '<div class="col m5 s12 ">'
            errors.error_log[environment].forEach((error, index) => {
                html += `<div class="row vertical-align-description">${error.description.length > 50 ? getBigDescriptionHtml(error) : getSmallDescriptionHtml(error)}</div>`
                if (index < nbr_errors-1)
                    html += '<hr>'
            })
            html += '</div>'
        return html 
}

function getErrorsGridHtml(errors) {
    let html = '';
    environments = ['Production','Staging','QA','Test']
    environments.forEach(environment => {
        if (environment in errors.error_log){    
            html += `<div class="row text-center ${environment} valign-wrapper">
                <div class="col center-align m2 s6 bold environment"><p>${environment}</p></div>`
            html += getHtmlErrors(errors.error_log[environment].length,errors,environment);
            html += '</div>';
        }
    })
    return html
}

async function renderLastErrors() {
    let errors = await getLastError()
    let error_informations = document.querySelector('.error-informations');
    error_informations.innerHTML = getErrorsGridHtml(errors);

    let time = document.querySelector('.p1');
    let time_sentence = `The following table recaps last errors that occured on servers on <div class="time-details">${errors.time}</div> with the automatic check :`;
    time.innerHTML = time_sentence;

    let refresh_button = document.querySelector('#refresh-button');
    let button_content = `<div class="row center-align">
                            <button id="button" class="btn waves-effect waves-light" onclick="getLastErrors()">Refresh here !</button>
                         </div>`
    refresh_button.innerHTML = button_content;
}

async function renderNewErrors() {
    let errors = await getNewError();

    let time = document.querySelector('.p1');
    let time_sentence = `The following table recaps last errors that occured on servers on <div class="time-details">${errors.time}</div> with your manual check :`;
    time.innerHTML = time_sentence;

    document.querySelector('.display-card').innerHTML = `<div class="card horizontal">
                                                            <div class="card-stacked">
                                                                <div class="card-content">
                                                                    <div class="row">
                                                                        <div class="col s12">
                                                                            <div id="errors-table" class="">
                                                                                <div class="row center bold">
                                                                                    <div class="col s2 Environment"></div>
                                                                                    <div class="col s5 URLs"></div>
                                                                                    <div class="col s5 Description"></div>
                                                                                </div>
                                                                                <div class="error-informations">`


    let error_informations = document.querySelector('.error-informations');
    error_informations.innerHTML = getErrorsGridHtml(errors);                                                                        
    document.querySelector('.Environment').innerHTML = 'Environment';
    document.querySelector('.URLs').innerHTML ='URLs';
    document.querySelector('.Description').innerHTML ='Description';
}

function showLoading(enabled=true) {
    document.getElementById("loader").style.visibility = enabled ? "visible" : "hidden"
    
}

function showGrid(enabled=true) {
    document.querySelector('#content').style.visibility = enabled ? "visible" : "hidden"
}

async function getLastErrors(){
    showGrid(false)
    showLoading()
    await renderLastErrors() 
    showLoading(false)
    showGrid()
}

async function runManualCheck(){
    let button = document.querySelector('#button')
    showGrid(false)
    showLoading()
    button.disabled = true;
    await renderNewErrors()
    button.disabled = false;
    showLoading(false)
    showGrid()
}

showLoading(false);