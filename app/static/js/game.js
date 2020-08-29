//on documet ready
$(document).ready(function () {
    
    var mana_slider = $("#mana")
    var spell_mana_slider = $("#spell_mana")
    var round_n_slider = $("#round_n")

    //registering slider stop event listener to send  and fetch results.
    mana_slider.slider().on('slideStop',function (event) {
        fetchCardResult()
    });

    spell_mana_slider.slider().on('slideStop',function (event) {
        fetchCardResult()
    });

    round_n_slider.slider().on('slideStop',function (event) {
        fetchCardResult() 
    });


});

//fetches current slider values
//performs ajax post to get new result
//refresh cards with new info
function fetchCardResult() {

    //retaining current slider values
    var mana_slider_val = $('#mana').slider('getValue')
    var spell_mana_slider_val = $('#spell_mana').slider('getValue')
    var round_n_slider_val = $('#round_n').slider('getValue')

    var post_data = {
        'mana':mana_slider_val,
        'spell_mana':spell_mana_slider_val,
        'round_n':round_n_slider_val
    }

    //ajax call to game update to fetch new results
    $('.loader').show()
    $.ajax({
        type: "POST",
        url: "/game_update",
        data: post_data,
        success: function (response) {
            refreshCards(response)
            $('.loader').hide()
        },
        error:function (e) {
            $('.loader').hide()
            alert('There was an error during the process!. Try again')
        }
    });

}

function refreshCards(response){
    
    //setting the deck count
    $('#deck_count').html(response.deck_count+' potential decks found. Displaying combined stats below:')

    //preparing html for respective cards
    var units_div_html = prepareDynamicHtml(response['units'])
    var fast_spells_div_html = prepareDynamicHtml(response['fast_spells'])
    var slow_spells_html = prepareDynamicHtml(response['slow_spells'])

    //removing previous cards
    $('#units_div').empty()
    $('#fast_spells_div').empty()
    $('#slow_spells_div').empty()

    //setting cards with new info
    $('#units_div').html(units_div_html)
    $('#fast_spells_div').html(fast_spells_div_html)
    $('#slow_spells_div').html(slow_spells_html)

}

function prepareDynamicHtml(response){
    var html = ''
    
    $.each(response, function (index, unit) { 
            html += '<div class="d-flex flex-row test-row">'
            html += '<div class="d-flex test_box">'
            var img = "'/static/img/small cards/"+unit['cardCode']+"_resized.jpg'"
            html += '<div class="d-flex test_card" style="background: linear-gradient(90deg, #c49250 30%, rgba(90, 184, 218, 0) 70%) repeat scroll 0% 0%, rgba(0, 0, 0, 0) url('+img+') no-repeat scroll right center;">'
            html += '<div class="d-flex my-0 mx-1 mana_cicrle"><strong>'+unit['cost']+'</strong></div>'
            html += '<p class="align-self-center m-0">'+unit['name']+'<br>'+unit['chance_string']+'</p>'
            html += '<div class="container-test test-responsive">'
            html +=' <div class="row justify-content-start">'
            html +='  <div class="col">'
            html +=' <img src="../static/img/full cards/'+unit['cardCode']+'_full.jpg" />'
            html +=' </div>'
            html +=' <div class="col detail_stats">'
            html +=' <ul class="">'
            html +=' <li>Deck Inclusion: '+unit['deck_chance_string'] +'</li>'
            html +=' <li>Expected Copies: '+unit['weighted_cards_string'] +'</li>'
            html +=' <li>Probability 0 drawn: '+unit['chance_string_0'] +'</li>'
            html +=' <li>Probability 1 drawn: '+unit['chance_string_1']+' </li>'
            html +=' <li>Probability 2 drawn: '+ unit['chance_string_2'] +'</li>'
            html +=' <li>Probability 3 drawn: '+ unit['chance_string_3'] +'</li>'
            html += '</ul>'
            html += '</div>'
            html += '</div>'
            html += '</div>'
            html += '</div>' 
            html += '</div>'
            html += '</div>'
         
    });
   return html
}