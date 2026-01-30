from faker import Faker
import random
from core.models import TableModel, ColumnModel

class FakeGenerator:
    def __init__(self, locale: str = "fr_FR"):
        self.fake = Faker(locale)

    def generate_rows(self, table: TableModel, count: int) -> list[dict]:
        """Generate 'count' rows of fake data for the given table."""
        rows = []
        for _ in range(count):
            row_data = {}
            for col in table.columns:
                # Skip Auto Increment usually (let DB handle it), 
                # but if we want to preview, we might just skip it for INSERTs
                if col.is_auto_increment:
                    continue
                
                val = self._generate_value_for_col(col)
                row_data[col.name] = str(val)
            rows.append(row_data)
        return rows

    def _generate_value_for_col(self, col: ColumnModel) -> any:
        name = col.name.lower()
        ctype = col.sql_type.upper()

        # 1. Detection by Name (Heuristics)
        if "email" in name or "mail" in name:
            return self.fake.email()
        
        if "prenom" in name or "firstname" in name:
            return self.fake.first_name()
        
        if "nom" in name or "lastname" in name or "surname" in name:
            return self.fake.last_name()
        
        if "tel" in name or "phone" in name:
            return self.fake.phone_number()
        
        if "adresse" in name or "address" in name or "street" in name:
            return self.fake.street_address()
        
        if "ville" in name or "city" in name:
            return self.fake.city()
            
        if "zip" in name or "postal" in name or "cp" in name:
            return self.fake.postcode()
        
        if "pays" in name or "country" in name:
            return self.fake.country()
            
        if "date" in name:
            if "naissance" in name or "birth" in name:
                return self.fake.date_of_birth()
            return self.fake.date_this_decade()
            
        if "description" in name or "comment" in name or "bio" in name:
            return self.fake.sentence(nb_words=10)
            
        if "titre" in name or "title" in name:
            return self.fake.sentence(nb_words=3).replace(".", "")
            
        if "login" in name or "user" in name or "pseudo" in name:
            return self.fake.user_name()
            
        if "pass" in name or "pwd" in name:
            return "P@ssw0rd123!" # Standard format often preferred over random mess
            
        if "url" in name or "site" in name or "link" in name:
            return self.fake.url()
        
        if "uuid" in name:
            return self.fake.uuid4()

        # 2. Detection by SQL Type
        if "INT" in ctype:
            if "age" in name:
                return random.randint(18, 90)
            if "annee" in name or "year" in name:
                return random.randint(1990, 2025)
            return random.randint(0, 1000)
            
        if "DECIMAL" in ctype or "FLOAT" in ctype or "MONEY" in ctype:
            if "prix" in name or "price" in name:
                return round(random.uniform(10.0, 500.0), 2)
            return round(random.uniform(0.0, 100.0), 2)
            
        if "BOOL" in ctype or "BIT" in ctype:
            return random.choice([0, 1])
            
        if "DATE" in ctype or "TIME" in ctype:
            return self.fake.date_this_year()

        # Fallback text
        return self.fake.word()
