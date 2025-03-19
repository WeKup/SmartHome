class NewsService:
    
    def get_all_news(self):
        return self._get_news_data()
    
    def get_latest_news(self, count=3):
        news = self._get_news_data()
        sorted_news = sorted(news, key=lambda x: x['date'], reverse=True)
        
        return sorted_news[:count]
    
    def _get_news_data(self):
        return [
            {
                'id': 1,
                'title': 'Bienvenue sur notre plateforme de maison connectée',
                'content': 'Nous sommes ravis de vous accueillir sur notre nouvelle plateforme de gestion de maison intelligente. Cette interface vous permet de contrôler tous vos objets connectés depuis un seul endroit, d\'optimiser votre consommation énergétique et de personnaliser votre expérience au quotidien.',
                'date': '2036-04-07',
            },
            {
                'id': 2,
                'title': 'Nouvelle mise à jour : contrôle vocal amélioré',
                'content': 'Notre dernière mise à jour améliore considérablement le contrôle vocal de vos appareils. Vous pouvez désormais utiliser des commandes plus naturelles et créer des scénarios personnalisés avec votre voix.',
                'date': '2036-04-14',
            },
            {
                'id': 3,
                'title': 'Conseils pour économiser l\'énergie',
                'content': 'Découvrez nos astuces pour réduire votre consommation énergétique grâce à votre maison connectée. Programmez vos thermostats intelligents, utilisez les modes d\'économie d\'énergie et consultez nos rapports détaillés.',
                'date': '2036-04-17',
            },
            {
                'id': 4,
                'title': 'Comment sécuriser votre maison intelligente',
                'content': 'La sécurité est primordiale dans une maison connectée. Voici nos conseils pour protéger vos appareils et vos données personnelles contre les accès non autorisés.',
                'date': '2036-04-22',
            },
            {
                'id': 5,
                'title': 'Nouveaux objets compatibles',
                'content': 'Nous avons élargi notre liste d\'objets compatibles ! Vérifiez si vos nouveaux appareils peuvent être intégrés à notre plateforme pour une expérience encore plus complète.',
                'date': '2036-04-29',
            }
        ]