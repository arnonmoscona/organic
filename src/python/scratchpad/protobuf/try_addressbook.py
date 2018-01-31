from protobuf.generated.addressbook_pb2 import Person

person = Person()
person.id = 1234
person.name = 'Joe Protobuf'
person.email = 'joe.protobuf@google.com'

phone = person.phones.add()
phone.number = '123-456-7890'
phone.type = Person.MOBILE

if person.IsInitialized():
    print('Initialized :-)\n')
    print(str(person))

    print('Serializing...')
    bytes = person.SerializeToString()
    print(f'Got length {len(bytes)}')
    print('Deserialising...')
    new_person = Person()
    new_person.ParseFromString(bytes)
    print('\nGot:\n')
    print(str(new_person))
    print(f'\nEqual? {person == new_person}')
else:
    print('Not initialized :-(')
