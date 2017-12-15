Base contracts for MVP1
#######################

Message contracts
*****************

* Messages are pure data
    * Message structure is specified using protobuf3 syntax regardless of whether or not an IDL
      compiler is used and regardless of whether or not protobuf is the serialization format.
    * Message semantics are expressed in MVP1 in plain natural language.
    * Message data constraints are expressed by natural language plus a validation Python function
      classifying messages as conforming or not.
* Messages are self-contained
    * Messages do not have a direct link to any data outside the message
    * All the semantics of a message are expressed by attributes of the messages and the named
      message type
        * Specifically, no control or transport layer data has any application semantics
        * The message type may imply some application level assumptions about the interaction model.
          For instance: Message of type `A` is a request, expecting a response formulated as a
          message of type `B`. Or Message of type `C` is broadcast on named P/S topic 'T1' and
          expresses unidirectional communication.
* Messages have no behavior
    * All behavior is accomplished by functions operatingh on messages
* Messages are immutable
    * Even if a message is technically mutable, there is no defind semantics or guarantees of
      what happens in the case of mutation.
    * The component controller and other parts of the system may not mutate a message except is
      well defined ways in order to provide a service to the component.
        * Example1: transport encryption
        * Example 2: transport integrity checks and anti-tampering signatures.
        * Example 3: application level security services, such as field level encryption, full
          state transfer security controls, etc.
        * In all such cases, transformations must be accomplished by producing new messages
          rather than mutation of messages.
* Messages are serializable to several formats
    * The message contract is on a deserialized form (may never have been serialized) and a
      functioning message in-process interaction must be capable of being accomplished with no
      serialization.
    * Deserialized messages from any format are semantically interchangeable
    * Message data access is only defined via a dot notation attribute access

Configuration semantics
***********************


Control/Application plane split
*******************************


Component controller to component implementation interface
**********************************************************


Controller to local machine environment interaction
***************************************************

