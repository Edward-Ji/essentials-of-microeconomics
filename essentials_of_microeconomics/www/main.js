$('a[data-bs-toggle="tab"]').on('shown.bs.tab', event => {
    const hash = $(event.target).attr('data-value');
    location.hash = hash;
});

const hash = window.location.hash;
if (hash) {
    const a = $('a[data-bs-toggle="tab"][data-value="' + hash.slice(1) + '"]');
    a.ready(() => a.tab('show'));
}
