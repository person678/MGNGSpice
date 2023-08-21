function [masking] = timeMultiplexing(inputSequence,sequenceLength,nodes,maskingType, maskingOffset)

switch(maskingType)
   
    case 'hold' % Sample and Hold

        masking = repelem (inputSequence,nodes);
        
    case 'binary' % Binary Weight Masking
        
        AinputSequence = repelem (inputSequence,nodes);
        r = 2* randi(2,nodes,1)-1 -2;
        Amasking = repmat(r,sequenceLength,1);
        
        if contains(maskingOffset, 'true')    
            % Offset
            masking = Amasking .* AinputSequence + AinputSequence;
        else
            % No-Offset
            masking = Amasking .* AinputSequence; 
        end

    case 'random' % Random Weight Masking
        
        AinputSequence = repelem (inputSequence,nodes);
        r = -1 + (1+1)*rand(nodes,1);
        Amasking = repmat(r,sequenceLength,1);
        
        if contains(maskingOffset, 'true') 
            % Offset
             masking = Amasking .* AinputSequence + AinputSequence;
        else
            % No-Offset
            masking = Amasking .* AinputSequence; % M * u
        end
        
        otherwise
        
        masking = [];

end