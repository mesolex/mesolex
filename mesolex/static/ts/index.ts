import * as jQuery from 'jquery';
import 'bootstrap/js/dist/dropdown';

import 'mesolex/scss/index.scss';

/**
 Ensure that the language selector links redirect to the appropriate translation
 for the active page.
 */
jQuery(($) => {
  $('#language-select button').one('click', function handleLgClick(e) {
    e.preventDefault();

    const $this = $(this);
    const translationUrl = $this.data('translation-url');
    const $form = $this.closest('form');
    const $next = $form.find('input[name="next"]');

    $next.val(translationUrl);
    $this.trigger('click');
  });
});
