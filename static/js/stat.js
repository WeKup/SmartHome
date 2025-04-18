document.addEventListener('DOMContentLoaded', function() {
    function debugLog(message, data = null) {
        console.log(`[STATS DEBUG] ${message}`);
        if (data) console.log(data);
    }

    function createChart(chartElement, chartType, labels, data, options = {}) {
        debugLog(`Tentative de création du graphique: ${chartElement.id}`);
        
        try {
            const ctx = chartElement.getContext('2d');

            const defaultOptions = {
                responsive: true,
                maintainAspectRatio: false,
                scales: chartType !== 'pie' && chartType !== 'doughnut' ? {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                } : {},
                plugins: chartType === 'doughnut' ? {
                    legend: {
                        position: 'right'
                    }
                } : {}
            };

            const mergedOptions = {...defaultOptions, ...options};

            debugLog(`Création du graphique ${chartElement.id}`, {
                type: chartType,
                labels: labels,
                data: data
            });

            new Chart(ctx, {
                type: chartType,
                data: {
                    labels: labels,
                    datasets: [{
                        label: chartElement.id,
                        data: data,
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.7)',
                            'rgba(255, 206, 86, 0.7)',
                            'rgba(75, 192, 192, 0.7)',
                            'rgba(153, 102, 255, 0.7)',
                            'rgba(255, 99, 132, 0.7)',
                            'rgba(255, 159, 64, 0.7)',
                            'rgba(199, 199, 199, 0.7)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: mergedOptions
            });

            debugLog(`Graphique ${chartElement.id} créé avec succès`);
        } catch (error) {
            debugLog(`ERREUR lors de la création du graphique: ${error}`);
        }
    }

    fetch('/admin/stats/data')
        .then(response => {
            debugLog('Réponse du serveur reçue');
            if (!response.ok) {
                throw new Error('Erreur de chargement des données');
            }
            return response.json();
        })
        .then(data => {
            console.log('Données reçues:', data);

            if (data.user_levels && data.user_levels.length) {
                console.log('Données des niveaux utilisateurs:', data.user_levels);
                const userLevelsCtx = document.getElementById('userLevelsChart');
                if (userLevelsCtx) {
                    const labels = data.user_levels.map(item => item[0]);
                    const counts = data.user_levels.map(item => item[1]);
                    console.log('Labels:', labels);
                    console.log('Counts:', counts);
                    
                    createChart(
                        userLevelsCtx, 
                        'doughnut', 
                        labels, 
                        counts
                    );
                } else {
                    console.error('Canvas userLevelsChart non trouvé');
                }
            } else {
                console.warn('Aucune donnée pour les niveaux utilisateurs');
            }

            if (data.objects_by_type && data.objects_by_type.length) {
                const objectsByTypeCtx = document.getElementById('objectsByTypeChart');
                if (objectsByTypeCtx) {
                    const labels = data.objects_by_type.map(item => item[0]);
                    const counts = data.objects_by_type.map(item => item[1]);
                    
                    createChart(
                        objectsByTypeCtx, 
                        'bar', 
                        labels, 
                        counts,
                        {
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Objets par type'
                                }
                            }
                        }
                    );
                }
            }
            if (data.conso && data.conso.length) {
                const conso = document.getElementById('conso');
                if (conso) {
                    const labels = data.conso.map(item => item[0]);
                    const consumptions = data.conso.map(item => item[1] || 0);
                    
                    createChart(
                        conso, 
                        'bar', 
                        labels, 
                        consumptions,
                        {
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'consommation des objet en W'
                                },
                            }
                        }
                    );
                }
            }
            if (data.temp && data.temp.length) {
                const temp = document.getElementById('temp');
                if (temp) {
                    const labels = data.temp.map(item => item[0]);
                    const consumptions = data.temp.map(item => item[1] || 0);
                    
                    createChart(
                        temp, 
                        'bar', 
                        labels, 
                        consumptions,
                        {
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'température des objet en °C'
                                },
                            }
                        }
                    );
                }
            }
            if (data.eau && data.eau.length) {
                const eau = document.getElementById('eau');
                if (eau) {
                    const labels = data.eau.map(item => item[0]);
                    const consumptions = data.eau.map(item => item[1] || 0);
                    
                    createChart(
                        eau, 
                        'bar', 
                        labels, 
                        consumptions,
                        {
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'consommation d eau en Litres des objets'
                                },
                            }
                        }
                    );
                }
            }
            if (data.gaz && data.gaz.length) {
                const gaz = document.getElementById('gaz');
                if (gaz) {
                    const labels = data.gaz.map(item => item[0]);
                    const consumptions = data.gaz.map(item => item[1] || 0);
                    
                    createChart(
                        gaz, 
                        'bar', 
                        labels, 
                        consumptions,
                        {
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'consommation en gaz des objet en m^3'
                                },
                            }
                        }
                    );
                }
            }
            if (data.autre && data.autre.length) {
                const autre = document.getElementById('autre');
                if (autre) {
                    const labels = data.autre.map(item => item[0]);
                    const consumptions = data.autre.map(item => item[1] || 0);
                    
                    createChart(
                        autre, 
                        'bar', 
                        labels, 
                        consumptions,
                        {
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Consommation autre des objet'
                                },
                            }
                        }
                    );
                }
            }
            if (data.service_stats) {
                const serviceStatsCtx = document.getElementById('serviceStatsChart');
                if (serviceStatsCtx) {
                    const labels = [
                        'Recherches', 
                        'Ajout Utilisateur', 
                        'Delete Utilisateur', 
                        'Ajout', 
                        'Ajout Room', 
                        'Ajout Type', 
                        'delete ', 
                        'Modifications', 
                        'modification d objet'
                    ];
                    const counts = [
                        data.service_stats.recherches || 0,
                        data.service_stats.ajout_utilisateurs || 0,
                        data.service_stats.delete_utilisateur || 0,
                        data.service_stats.ajout_objet || 0,
                        data.service_stats.ajout_room || 0,
                        data.service_stats.ajout_type || 0,
                        data.service_stats.delete || 0,
                        data.service_stats.modifications || 0,
                        data.service_stats.modifObjet || 0
                    ];
                    
                    createChart(
                        serviceStatsCtx, 
                        'pie', 
                        labels, 
                        counts,
                        {
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Statistiques des Services'
                                }
                            }
                        }
                    );
                }
            }
            if (data.objects_by_room && data.objects_by_room.length) {
                const objectsByRoomCtx = document.getElementById('objectsByRoomChart');
                if (objectsByRoomCtx) {
                    const labels = data.objects_by_room.map(item => item[0]);
                    const counts = data.objects_by_room.map(item => item[1]);
                    
                    createChart(
                        objectsByRoomCtx, 
                        'bar', 
                        labels, 
                        counts,
                        {
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Objets par pièce'
                                }
                            }
                        }
                    );
                }
            }

            if (data.connexions_by_day && data.connexions_by_day.length) {
                const connexionsByDayChart = document.getElementById('connexionsByDayChart');
                if (connexionsByDayChart) {
                    const labels = data.connexions_by_day.map(item => item[0]);
                    const counts = data.connexions_by_day.map(item => item[1]);
                    
                    createChart(
                        connexionsByDayChart, 
                        'line', 
                        labels, 
                        counts,
                        {
                            plugins: {
                                title: {
                                    display: true,
                                    text: 'Connexion les 30 derniers jours'
                                }
                            }
                        }
                    );
                }
            }

            debugLog('Traitement des statistiques terminé');
        })
        .catch(error => {
            debugLog('ERREUR FATALE lors du chargement des statistiques:', error);
            
            const errorContainer = document.createElement('div');
            errorContainer.classList.add('alert', 'alert-danger');
            errorContainer.textContent = `Impossible de charger les statistiques : ${error.message}`;
            document.body.insertBefore(errorContainer, document.body.firstChild);
        });
});