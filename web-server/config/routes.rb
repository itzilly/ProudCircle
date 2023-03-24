Rails.application.routes.draw do
  # get 'leaderboard/index'
  # Define your application routes per the DSL in https://guides.rubyonrails.org/routing.html
  get "/articles", to: "articles#index"

  get '/leaderboards(/:type)', to: 'leaderboards#index', as: 'leaderboards', start_date: /\d{4}-\d{2}-\d{2}/, end_date: /\d{4}-\d{2}-\d{2}/

  # Defines the root path route ("/")
  # root "articles#index"
end
