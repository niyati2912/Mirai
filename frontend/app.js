let essChart = null;
let forecastChart = null;
let modelChart = null;


/* =========================================================
   NAVIGATION
========================================================= */

const navButtons = document.querySelectorAll("[data-page]");
const pages = document.querySelectorAll(".page");


navButtons.forEach((button) => {

    button.addEventListener("click", () => {

        const pageName = button.dataset.page;

        if (!pageName) return;

        pages.forEach((page) => {
            page.classList.remove("active-page");
        });


        const targetPage = document.getElementById(
            `${pageName}-page`
        );

        if (targetPage) {
            targetPage.classList.add("active-page");
        }


        document
            .querySelectorAll(".top-nav-item")
            .forEach((item) => {

                item.classList.toggle(
                    "active",
                    item.dataset.page === pageName
                );

            });


        document
            .querySelectorAll(".sidebar-item[data-page]")
            .forEach((item) => {

                item.classList.toggle(
                    "active",
                    item.dataset.page === pageName
                );

            });


        requestAnimationFrame(() => {

            if (pageName === "dashboard") {
                renderEssChart();
            }

            if (pageName === "forecast") {
                renderForecastChart();
            }

            if (pageName === "models") {
                renderModelChart();
            }

        });

    });

});


/* =========================================================
   COMMON CHART SETTINGS
========================================================= */

Chart.defaults.color = "#81909c";

Chart.defaults.font.family =
    '"JetBrains Mono", monospace';


const gridColor = "rgba(90, 110, 122, 0.13)";


/* =========================================================
   DASHBOARD ESS CHART
========================================================= */

function renderEssChart() {

    const canvas = document.getElementById("essChart");

    if (!canvas) return;


    if (essChart) {
        essChart.destroy();
    }


    essChart = new Chart(canvas, {

        type: "line",

        data: {

            labels: [
                "2021",
                "",
                "2022",
                "",
                "2023",
                "",
                "2024",
                "",
                "2025",
                "",
                "2026"
            ],

            datasets: [

                {

                    label: "Economic Stress Score",

                    data: [
                        14,
                        22,
                        36,
                        40,
                        34,
                        22,
                        30,
                        58,
                        66,
                        50,
                        54
                    ],

                    borderColor: "#2ba4e1",

                    borderWidth: 2,

                    tension: 0.45,

                    fill: true,

                    backgroundColor:
                        "rgba(35, 153, 213, 0.07)",

                    pointRadius: 0,

                    pointHoverRadius: 4

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {
                    display: false
                },

                tooltip: {

                    backgroundColor: "#111b22",

                    borderColor: "#2b3943",

                    borderWidth: 1,

                    titleColor: "#dce7ed",

                    bodyColor: "#aebcc5"

                }

            },

            scales: {

                x: {

                    grid: {
                        display: false
                    },

                    ticks: {

                        color: "#82919a",

                        font: {
                            size: 8
                        }

                    },

                    border: {
                        color: "#26323a"
                    }

                },

                y: {

                    min: 0,
                    max: 80,

                    ticks: {

                        stepSize: 20,

                        color: "#82919a",

                        font: {
                            size: 8
                        }

                    },

                    grid: {
                        color: gridColor
                    },

                    border: {
                        display: false
                    }

                }

            }

        }

    });

}


/* =========================================================
   FORECAST CHART
========================================================= */

function renderForecastChart() {

    const canvas = document.getElementById("forecastChart");

    if (!canvas) return;


    if (forecastChart) {
        forecastChart.destroy();
    }


    forecastChart = new Chart(canvas, {

        type: "line",

        data: {

            labels: [
                "Q1 '22",
                "",
                "Q3 '22",
                "",
                "Q1 '23",
                "",
                "Q3 '23",
                "",
                "Q1 '24"
            ],

            datasets: [

                {

                    label: "Actual ESS",

                    data: [
                        1.2,
                        1.5,
                        2.9,
                        2.2,
                        1.8,
                        3.5,
                        3.1,
                        3.0,
                        1.4
                    ],

                    borderColor: "#8bc5e8",

                    borderWidth: 2,

                    tension: 0,

                    pointRadius: 0

                },


                {

                    label: "Conventional",

                    data: [
                        1.1,
                        1.4,
                        1.9,
                        2.1,
                        1.9,
                        2.5,
                        2.7,
                        2.6,
                        1.9
                    ],

                    borderColor: "#879299",

                    borderWidth: 1,

                    borderDash: [4, 4],

                    tension: 0,

                    pointRadius: 0

                },


                {

                    label: "Conv + Behavioral",

                    data: [
                        1.15,
                        1.4,
                        2.6,
                        2.15,
                        1.85,
                        3.2,
                        3.0,
                        2.9,
                        1.6
                    ],

                    borderColor: "#d89c4e",

                    borderWidth: 1.5,

                    borderDash: [3, 3],

                    tension: 0,

                    pointRadius: 0

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {
                    display: false
                }

            },

            scales: {

                x: {

                    grid: {
                        display: false
                    },

                    ticks: {

                        color: "#8b9aa4",

                        font: {
                            size: 8
                        }

                    },

                    border: {
                        color: "#35424a"
                    }

                },

                y: {

                    min: 0,
                    max: 4,

                    ticks: {

                        stepSize: 1,

                        color: "#8b9aa4",

                        font: {
                            size: 8
                        }

                    },

                    grid: {
                        color: gridColor
                    },

                    border: {
                        display: false
                    }

                }

            }

        }

    });

}


/* =========================================================
   MODEL COMPARISON CHART
========================================================= */

function renderModelChart() {

    const canvas = document.getElementById("modelChart");

    if (!canvas) return;


    if (modelChart) {
        modelChart.destroy();
    }


    modelChart = new Chart(canvas, {

        type: "bar",

        data: {

            labels: [
                "Baseline",
                "Conventional",
                "Conv + Beh"
            ],

            datasets: [

                {

                    label: "MAE",

                    data: [
                        4.338,
                        3.095,
                        3.095
                    ],

                    backgroundColor: [
                        "#303a43",
                        "#6f9bb8",
                        "#d19b62"
                    ],

                    borderWidth: 0,

                    barPercentage: 0.6

                },


                {

                    label: "RMSE",

                    data: [
                        5.451,
                        3.811,
                        3.811
                    ],

                    backgroundColor: [
                        "#3a444d",
                        "#83abc5",
                        "#b98d5e"
                    ],

                    borderWidth: 0,

                    barPercentage: 0.6

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    position: "bottom",

                    labels: {

                        color: "#a3b0b8",

                        boxWidth: 8,

                        font: {
                            size: 8
                        }

                    }

                }

            },

            scales: {

                x: {

                    grid: {
                        display: false
                    },

                    ticks: {

                        color: "#a2afb8",

                        font: {
                            size: 8
                        }

                    },

                    border: {
                        color: "#45515a"
                    }

                },

                y: {

                    beginAtZero: true,

                    max: 6,

                    ticks: {

                        stepSize: 2,

                        color: "#87959f",

                        font: {
                            size: 8
                        }

                    },

                    grid: {
                        color: gridColor
                    },

                    border: {
                        display: false
                    }

                }

            }

        }

    });

}


/* =========================================================
   INITIAL PAGE
========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    renderEssChart();

});