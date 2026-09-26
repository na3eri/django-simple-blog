const searchForm = document.getElementById("searchForm");
const pageLinks = document.querySelectorAll(".page-link");


/* =========================
   Search
========================= */

if (searchForm) {

    searchForm.addEventListener("submit", function (e) {

        e.preventDefault();

        const searchInput = document.getElementById("searchInput");
        const search = searchInput.value.trim();

        const url = new URL(
            searchForm.action,
            window.location.origin
        );

        if (search) {
            url.searchParams.set("q", search);
        }

        window.location.href = url.toString();

    });

}


/* =========================
   Pagination
========================= */

pageLinks.forEach(function (link) {

    link.addEventListener("click", function (e) {

        e.preventDefault();

        const params = new URLSearchParams(window.location.search);

        const page = this.dataset.page;

        params.set("page", page);

        const queryString = params.toString();

        window.location.href = queryString
            ? `${window.location.pathname}?${queryString}`
            : window.location.pathname;

    });

});