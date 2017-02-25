import yaml


class Generator(object):
    __create_table = '''CREATE TABLE "{table}" (
    "{table}_id" SERIAL NOT NULL,
    {columns}
    "{table}_created" timestamp default CURRENT_TIMESTAMP,
    "{table}_updated" timestamp default CURRENT_TIMESTAMP,
    PRIMARY KEY({table}_id)\n);\n\n'''

    __create_join_table = '''CREATE TABLE "{table1}__{table2}" (
    "{table1}_id" INTEGER NOT NULL,
    "{table2}_id" INTEGER NOT NULL,
    PRIMARY KEY ("{table1}_id", "{table2}_id")\n);\n\n'''

    __create_column = '"{table_name}_{column_name}" {data_type} NOT NULL,'

    __alter_table = '''ALTER TABLE "{child}" ADD "{parent}_id" integer NOT NULL,
    ADD CONSTRAINT "fk_{child}_{parent}_id" FOREIGN KEY ("{parent}_id")
    REFERENCES "{parent}" ("{parent}_id");\n\n'''

    __alter_join_table = '''ALTER TABLE "{table1}__{table2}" ADD CONSTRAINT "fk_{table1}{table2}_{table1}_id" FOREIGN KEY ("{table1}_id")
    REFERENCES "{table1}" ("{table1}_id");

ALTER TABLE "{table1}__{table2}" ADD CONSTRAINT "fk_{table1}{table2}_{table2}_id" FOREIGN KEY ("{table2}_id")
    REFERENCES "{table2}" ("{table2}_id");\n\n'''

    __create_trigger = '''CREATE OR REPLACE FUNCTION update_time()
RETURNS TRIGGER AS $$
BEGIN
    NEW.{table}_updated = now();
    RETURN NEW;
END;
$$ language 'plpgsql';
CREATE TRIGGER update_time BEFORE UPDATE ON "{table}" FOR EACH ROW EXECUTE PROCEDURE update_time();\n\n'''

    def __init__(self):
        self.__tables = set()
        self.__triggers = set()
        self.__alters = set()
        self.__schema = {}

    def create_tables(self):
        for entity in self.__schema:
            columns = '\n\t\t'.join(self.create_columns(entity))
            self.__tables.add(self.__create_table.format(table=entity.lower(), columns=columns))
            self.create_triggers(entity)
            self.create_relations(entity)

    def create_columns(self, entity):
        for column, data_type in self.__schema[entity]['fields'].items():
            yield self.__create_column.format(table_name=entity.lower(), column_name=column, data_type=data_type)

    def create_triggers(self, entity):
        self.__triggers.add(self.__create_trigger.format(table=entity.lower()))

    def create_relations(self, entity):
        if 'relations' in self.__schema[entity]:
            for foreign_table, relation in self.__schema[entity]['relations'].items():
                if relation == 'one' and self.__schema[foreign_table]['relations'][entity] == 'many':
                    self.create_one_to_many(entity.lower(), foreign_table.lower())
                if relation == 'many' and self.__schema[foreign_table]['relations'][entity] == 'many':
                    self.create_many_to_many([entity.lower(), foreign_table.lower()])
        else:
            raise Exception('Relations not found!')

    def create_many_to_many(self, join_table):
        join_table = sorted(join_table)
        self.__tables.add(self.__create_join_table.format(table1=join_table[0], table2=join_table[1]))
        self.__alters.add(self.__alter_join_table.format(table1=join_table[0], table2=join_table[1]))

    def create_one_to_many(self, child, parent):
        self.__alters.add(self.__alter_table.format(child=child, parent=parent))

    def generate_ddl(self, config):
        self.__schema = self.parse_config(config)
        if self.__schema:
            self.create_tables()
        else:
            raise ValueError('Empty config file')

    def parse_config (self, file_name):
        with open(file_name) as f:
            return yaml.load(f)

    def write_dump(self):
        with open('query.sql', 'w+') as f:
            f.write(''.join(self.__tables))
            f.write(''.join(self.__alters))
            f.write(''.join(self.__triggers))


def main ():
    g = Generator()
    g.generate_ddl('db_config.yaml')
    g.write_dump()


if __name__ == '__main__':
    main()