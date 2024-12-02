odoo.define('rdp_website_snippet.dynamic_slider', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var rpc = require('web.rpc');

    $(document).ready(function () {
        ajax.jsonRpc('/latest_elearning_courses', 'call', {}).then(function (data) {
            var carouselInner = $('#CarouselInnerId');
            var totalItems = data.length;
            var itemsPerSlide = 3;
            var currentSlide = 0;

            if (carouselInner) {
                for (var i = 0; i < totalItems; i += itemsPerSlide) {
                    var activeClass = (i === 0) ? 'active' : '';
                    var carouselItem = `<div class="carousel-item carousel-item-blog ${activeClass}"><div class="row">`;
                    for (var j = i; j < i + itemsPerSlide && j < totalItems; j++) {
                        var item = data[j];
                        carouselItem += `
                            <div class="col-md-4 slider_data" style="width: 500px; height: 250px; padding: 15px; margin-bottom: 20px;">
                                <a href="${item.url}" class="card h-100 shadow-sm" style="text-decoration: none;">
                                    <div class="card-body text-center" style="background-color: #000000;">
                                        <h5 class="card-title" style="background-color: #000000; color: white;">${item.name}</h5>
                                    </div>
                                </a>
                            </div>`;
                    }
                    carouselItem += `
                        </div>  <!-- row -->
                    </div>  <!-- carousel-item -->`;
                    carouselInner.append(carouselItem);
                }
            }

            var slideIndex = 1;
            showSlides(slideIndex);

            $('#prevButton').on('click', function () {
                plusSlides(-1);
            });

            $('#nextButton').on('click', function () {
                plusSlides(1);
            });

            function plusSlides(n) {
                showSlides(slideIndex += n);
            }

            function showSlides(n) {
                var slides = $('.carousel-item-blog');
                if (n > slides.length) {
                    slideIndex = 1;
                }
                if (n < 1) {
                    slideIndex = slides.length;
                }
                slides.each(function (index) {
                    $(this).removeClass('active');
                    $(this).css('display', 'none');
                });
                slides.eq(slideIndex - 1).addClass('active');
                slides.eq(slideIndex - 1).css('display', 'block');
            }
        });
    });
});
