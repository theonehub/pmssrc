"""
Perquisites Entity
Represents various perquisites and their tax treatment
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from app.domain.value_objects.money import Money


@dataclass
class Perquisites:
    """Perquisites entity containing all perquisite components."""
    
    # Accommodation perquisites
    rent_free_accommodation: Money = Money.zero()
    concessional_accommodation: Money = Money.zero()
    
    # Vehicle perquisites
    car_perquisite: Money = Money.zero()
    driver_perquisite: Money = Money.zero()
    fuel_perquisite: Money = Money.zero()
    
    # Education perquisites
    education_perquisite: Money = Money.zero()
    
    # Domestic servant perquisites
    domestic_servant_perquisite: Money = Money.zero()
    
    # Gas, electricity, water perquisites
    utility_perquisite: Money = Money.zero()
    
    # Interest free/concessional loan perquisites
    loan_perquisite: Money = Money.zero()
    
    # Stock option perquisites
    esop_perquisite: Money = Money.zero()
    
    # Club membership perquisites
    club_membership_perquisite: Money = Money.zero()
    
    # Other perquisites
    other_perquisites: Money = Money.zero()
    
    def get_total_perquisites(self) -> Money:
        """Get total of all perquisites."""
        return (
            self.rent_free_accommodation
            .add(self.concessional_accommodation)
            .add(self.car_perquisite)
            .add(self.driver_perquisite)
            .add(self.fuel_perquisite)
            .add(self.education_perquisite)
            .add(self.domestic_servant_perquisite)
            .add(self.utility_perquisite)
            .add(self.loan_perquisite)
            .add(self.esop_perquisite)
            .add(self.club_membership_perquisite)
            .add(self.other_perquisites)
        )
    
    def calculate_rent_free_accommodation(self,
                                        basic_salary: Money,
                                        dearness_allowance: Money,
                                        city_population: int) -> Money:
        """
        Calculate rent-free accommodation perquisite.
        
        Args:
            basic_salary: Basic salary
            dearness_allowance: Dearness allowance
            city_population: Population of the city
            
        Returns:
            Money: Perquisite value
        """
        # Calculate salary for perquisite
        salary = basic_salary.add(dearness_allowance)
        
        # Determine percentage based on city population
        if city_population > 4000000:  # Metro cities
            percentage = Decimal('15')
        elif city_population > 1000000:  # Other cities
            percentage = Decimal('10')
        else:  # Other areas
            percentage = Decimal('7.5')
        
        return salary.percentage(percentage)
    
    def calculate_concessional_accommodation(self,
                                           basic_salary: Money,
                                           dearness_allowance: Money,
                                           city_population: int,
                                           rent_paid: Money) -> Money:
        """
        Calculate concessional accommodation perquisite.
        
        Args:
            basic_salary: Basic salary
            dearness_allowance: Dearness allowance
            city_population: Population of the city
            rent_paid: Rent paid by employee
            
        Returns:
            Money: Perquisite value
        """
        # Calculate rent-free perquisite
        rent_free = self.calculate_rent_free_accommodation(
            basic_salary,
            dearness_allowance,
            city_population
        )
        
        # Subtract rent paid
        if rent_paid.is_less_than(rent_free):
            return rent_free.subtract(rent_paid)
        else:
            return Money.zero()
    
    def calculate_car_perquisite(self,
                               car_value: Money,
                               car_owned_by: str,
                               car_used_by: str) -> Money:
        """
        Calculate car perquisite.
        
        Args:
            car_value: Value of the car
            car_owned_by: Who owns the car (employer/employee)
            car_used_by: Who uses the car (employee/employer/both)
            
        Returns:
            Money: Perquisite value
        """
        if car_owned_by == "employer":
            if car_used_by == "employee":
                return car_value.percentage(Decimal('2.5'))  # 2.5% of car value
            elif car_used_by == "both":
                return car_value.percentage(Decimal('1.875'))  # 1.875% of car value
            else:
                return Money.zero()
        else:
            return Money.zero()
    
    def calculate_driver_perquisite(self,
                                  driver_salary: Money,
                                  driver_owned_by: str) -> Money:
        """
        Calculate driver perquisite.
        
        Args:
            driver_salary: Salary of the driver
            driver_owned_by: Who employs the driver (employer/employee)
            
        Returns:
            Money: Perquisite value
        """
        if driver_owned_by == "employer":
            return driver_salary
        else:
            return Money.zero()
    
    def calculate_fuel_perquisite(self,
                                fuel_expense: Money,
                                car_owned_by: str,
                                car_used_by: str) -> Money:
        """
        Calculate fuel perquisite.
        
        Args:
            fuel_expense: Fuel expense amount
            car_owned_by: Who owns the car (employer/employee)
            car_used_by: Who uses the car (employee/employer/both)
            
        Returns:
            Money: Perquisite value
        """
        if car_owned_by == "employer":
            if car_used_by == "employee":
                return fuel_expense
            elif car_used_by == "both":
                return fuel_expense.percentage(Decimal('50'))
            else:
                return Money.zero()
        else:
            return Money.zero()
    
    def calculate_education_perquisite(self,
                                     education_expense: Money,
                                     school_type: str) -> Money:
        """
        Calculate education perquisite.
        
        Args:
            education_expense: Education expense amount
            school_type: Type of school (government/private)
            
        Returns:
            Money: Perquisite value
        """
        if school_type == "government":
            return Money.zero()
        else:
            return education_expense.percentage(Decimal('50'))
    
    def calculate_loan_perquisite(self,
                                loan_amount: Money,
                                interest_rate: Decimal,
                                market_rate: Decimal) -> Money:
        """
        Calculate interest free/concessional loan perquisite.
        
        Args:
            loan_amount: Loan amount
            interest_rate: Interest rate charged
            market_rate: Market interest rate
            
        Returns:
            Money: Perquisite value
        """
        if interest_rate < market_rate:
            interest_difference = market_rate - interest_rate
            return loan_amount.percentage(interest_difference)
        else:
            return Money.zero()
    
    def calculate_esop_perquisite(self,
                                fair_market_value: Money,
                                exercise_price: Money,
                                number_of_shares: int) -> Money:
        """
        Calculate ESOP perquisite.
        
        Args:
            fair_market_value: Fair market value per share
            exercise_price: Exercise price per share
            number_of_shares: Number of shares exercised
            
        Returns:
            Money: Perquisite value
        """
        if fair_market_value.is_greater_than(exercise_price):
            difference = fair_market_value.subtract(exercise_price)
            return difference.multiply(Decimal(str(number_of_shares)))
        else:
            return Money.zero() 