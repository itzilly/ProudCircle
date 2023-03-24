# class LeaderboardsController < ApplicationController
#   def get_daily_leaderboard_data
#     # This is a temporary function that returns some dummy data for the daily leaderboard
#     [
#       { name: "Player 1", score: 100 },
#       { name: "Player 2", score: 90 },
#       { name: "Player 3", score: 80 },
#       { name: "Player 4", score: 70 },
#       { name: "Player 5", score: 60 }
#     ]
#   end
#
#   def get_weekly_leaderboard_data
#     # This is a temporary function that returns some dummy data for the weekly leaderboard
#     [
#       { name: "Player 1", score: 500 },
#       { name: "Player 2", score: 450 },
#       { name: "Player 3", score: 400 },
#       { name: "Player 4", score: 350 },
#       { name: "Player 5", score: 300 }
#     ]
#   end
#
#   def get_monthly_leaderboard_data
#     # This is a temporary function that returns some dummy data for the monthly leaderboard
#     [
#       { name: "Player 1", score: 2000 },
#       { name: "Player 2", score: 1800 },
#       { name: "Player 3", score: 1600 },
#       { name: "Player 4", score: 1400 },
#       { name: "Player 5", score: 1200 }
#     ]
#   end
#
#   def get_yearly_leaderboard_data
#     # This is a temporary function that returns some dummy data for the yearly leaderboard
#     [
#       { name: "Player 1", score: 10000 },
#       { name: "Player 2", score: 9000 },
#       { name: "Player 3", score: 8000 },
#       { name: "Player 4", score: 7000 },
#       { name: "Player 5", score: 6000 }
#     ]
#   end
#
#   def get_lifetime_leaderboard_data
#     # This is a temporary function that returns some dummy data for the lifetime leaderboard
#     [
#       { name: "Player 1", score: 50000 },
#       { name: "Player 2", score: 45000 },
#       { name: "Player 3", score: 40000 },
#       { name: "Player 4", score: 35000 },
#       { name: "Player 5", score: 30000 }
#     ]
#   end
#
#   def index
#     type = params[:type] || 'monthly'
#     @start_date = params[:start_date]
#     @end_date = params[:end_date]
#     case type
#     when 'daily'
#       @leaderboard_type = 'Daily'
#       # Get data for the daily leaderboard
#       @leaderboard_data = get_daily_leaderboard_data
#     when 'weekly'
#       @leaderboard_type = 'Weekly'
#       # Get data for the weekly leaderboard
#       @leaderboard_data = get_weekly_leaderboard_data
#     when 'monthly'
#       @leaderboard_type = 'Monthly'
#       # Get data for the monthly leaderboard
#       @leaderboard_data = get_monthly_leaderboard_data
#     when 'yearly'
#       @leaderboard_type = 'Yearly'
#       # Get data for the yearly leaderboard
#       @leaderboard_data = get_yearly_leaderboard_data
#     when 'lifetime'
#       @leaderboard_type = 'Lifetime'
#       # Get data for the lifetime leaderboard
#       @leaderboard_data = get_lifetime_leaderboard_data
#     else
#       @leaderboard_type = 'Default - Monthly'
#       # Get data for default leaderboard (monthly)
#       @leaderboard_data = get_monthly_leaderboard_data
#     end
#   end
# end

class LeaderboardsController < ApplicationController
  def index
    type = params[:type] || ""

    # Default Start Date
    start_date_param = params[:start_date]
    if start_date_param.nil?
      @start_date = Date.parse("01/01/2023")
    else
      @start_date = Date.parse(start_date_param.to_s)
    end

    # Default End Date
    end_date_param = params[:end_date]
    if end_date_param.nil?
      @end_date = Date.today
    else
      @end_date = Date.parse(end_date_param.to_s)
    end

    where_clause = get_where_clause(type, @start_date, @end_date)
    command = "SELECT uuid, SUM(amount) as total_exp FROM expHistory#{where_clause} GROUP BY uuid ORDER BY total_exp DESC"
    puts "\nCommand: #{command}"
    @leaderboard_type = type.capitalize || 'Monthly'
    path ="O:\\Python Programming\\ProudCircle\\web-server\\proudcircle.db"
    db = SQLite3::Database.new path
    @leaderboard_data = db.execute(command)
  end

  private

  def get_where_clause(type, start_date, end_date)
    # Where Clause Builder
    case type
    when nil, ''
      where_clause = ""
      puts "Nil, ''"
    when 'daily'
      where_clause = " WHERE (date = #{end_date.strftime("%Y-%m-%d")})"
      puts "Daily!"
    when 'weekly'
      date_today = start_date.strftime("%Y-%m-%d")
      seven_days_ago = (Time.now - 7*24*60*60).strftime("%Y-%m-%d")
      where_clause = " WHERE (date BETWEEN #{seven_days_ago} AND #{date_today})"
      puts "Weekly!"
    when 'monthly'
      date_today = start_date.strftime("%Y-%m-%d")
      first_day_of_month = start_date.beginning_of_month
      where_clause = " WHERE (date BETWEEN #{first_day_of_month} AND #{date_today})"
      puts "Monthly!"
    when 'yearly'
      date_today = start_date.strftime("%Y-%m-%d")
      first_day_of_year = date_today.beginning_of_year
      where_clause = " WHERE (date BETWEEN #{first_day_of_year} AND #{date_today})"
      puts "Yearly!"
    when 'lifetime'
      where_clause = ""
      puts "Yearly!"
    else
      where_clause = " WHERE (date BETWEEN #{start_date.strftime("%Y-%m-%d")} AND #{end_date.strftime("%Y-%m-%d")})"
      puts "Else"
    end
    where_clause
  end
end