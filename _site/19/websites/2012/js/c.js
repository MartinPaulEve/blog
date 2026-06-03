Cufon.replace('#main h2, #main h3');


			var onMouseOutOpacity = 0.67;


			$(document).ready(function() {

			$('#thumbs ul.thumbs li').css('opacity', onMouseOutOpacity)
				.hover(
					function () {
						$(this).not('.selected').fadeTo('fast', 1.0);
					}, 
					function () {
						$(this).not('.selected').fadeTo('fast', onMouseOutOpacity);
					}
				);
				// Initialize Advanced Galleriffic Gallery
				var galleryAdv = $('#gallery').galleriffic('#thumbs', {
					delay:                  2000,
					numThumbs:              12,
					preloadAhead:           10,
					enableTopPager:         true,
					enableBottomPager:      false,
					imageContainerSel:      '#slideshow',
					controlsContainerSel:   '#controls',
					captionContainerSel:    '#caption',
					loadingContainerSel:    '#loading',
					renderSSControls:       true,
					renderNavControls:      true,
					playLinkText:           'Play Slideshow',
					pauseLinkText:          'Pause Slideshow',
					prevLinkText:           '&lsaquo; Previous Photo',
					nextLinkText:           'Next Photo &rsaquo;',
					nextPageLinkText:       'Next &rsaquo;',
					prevPageLinkText:       '&lsaquo; Prev',
					enableHistory:          true,
					autoStart:              false,
					onChange:               function(prevIndex, nextIndex) {
						$('#thumbs ul.thumbs').children()
							.eq(prevIndex).fadeTo('fast', onMouseOutOpacity).end()
							.eq(nextIndex).fadeTo('fast', 1.0);
					},
					onTransitionOut:        function(callback) {
						$('#caption').fadeTo('fast', 0.0);
						$('#slideshow').fadeTo('fast', 0.0, callback);
					},
					onTransitionIn:         function() {
						$('#slideshow').fadeTo('fast', 1.0);
						$('#caption').fadeTo('fast', 1.0);
					},
					onPageTransitionOut:    function(callback) {
						$('#thumbs ul.thumbs').fadeTo('fast', 0.0, callback);
					},
					onPageTransitionIn:     function() {
						$('#thumbs ul.thumbs').fadeTo('fast', 1.0);
					}
				});
			});